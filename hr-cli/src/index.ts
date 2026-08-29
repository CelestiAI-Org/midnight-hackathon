// This file is part of the HR salary verification MVP, adapted from
// midnightntwrk/example-bboard.
// Copyright (C) Midnight Foundation
// SPDX-License-Identifier: Apache-2.0

/*
 * This file is the main driver for the HR salary verification CLI.
 * The entry point is the run function, at the end of the file.
 * We expect the startup files (standalone.ts, preview.ts, preprod.ts) to
 * call run with some specific configuration that sets the network addresses
 * of the servers this file relies on.
 */

import { createInterface, type Interface } from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import { WebSocket } from 'ws';
import {
  HRAPI,
  type HRDerivedState,
  hrPrivateStateKey,
  type HRProviders,
  type DeployedHRContract,
  type PrivateStateId,
} from '../../api/src/index';
import { type WalletFacade } from '@midnight-ntwrk/wallet-sdk-facade';
import { ledger, type Ledger } from '../../contract/src/managed/hr-verification/contract/index.js';
import { NodeZkConfigProvider } from '@midnight-ntwrk/midnight-js-node-zk-config-provider';
import { indexerPublicDataProvider } from '@midnight-ntwrk/midnight-js-indexer-public-data-provider';
import { httpClientProofProvider } from '@midnight-ntwrk/midnight-js-http-client-proof-provider';
import { type Logger } from 'pino';
import { type Config, StandaloneConfig } from './config.js';
import { levelPrivateStateProvider } from '@midnight-ntwrk/midnight-js-level-private-state-provider';
import { type ContractAddress } from '@midnight-ntwrk/midnight-js-protocol/compact-runtime';
import { assertIsContractAddress, toHex } from '@midnight-ntwrk/midnight-js-utils';
import { TestEnvironment } from '@midnight-ntwrk/testkit-js';
import { MidnightWalletProvider } from './midnight-wallet-provider';
import { randomBytes } from '../../api/src/utils';
import { unshieldedToken } from '@midnight-ntwrk/midnight-js-protocol/ledger';
import { syncWallet, waitForUnshieldedFunds } from './wallet-utils';
import { generateDust } from './generate-dust';
import { HRPrivateState } from '../../contract/src/witnesses.js';

// @ts-expect-error: It's needed to enable WebSocket usage through apollo
globalThis.WebSocket = WebSocket;

/* **********************************************************************
 * getHRLedgerState: a helper that queries the current state of
 * the data on the ledger, for a specific HR verification contract.
 * The only field on this ledger is `verified` — the disclosed boolean
 * result of the most recent verifySalary call. The candidate's salary
 * never appears here.
 */

export const getHRLedgerState = async (
  providers: HRProviders,
  contractAddress: ContractAddress,
): Promise<Ledger | null> => {
  assertIsContractAddress(contractAddress);
  const contractState = await providers.publicDataProvider.queryContractState(contractAddress);
  return contractState != null ? ledger(contractState.data) : null;
};

/* **********************************************************************
 * readSalary / readBudget: prompt helpers. The salary is read once,
 * at deploy/join time, and is never echoed back or logged again.
 */

const readSalary = async (rli: Interface): Promise<bigint> => {
  const raw = await rli.question('Enter candidate salary (private, never displayed again): ');
  const value = BigInt(raw.trim());
  if (value < 0n) {
    throw new Error('Salary must be a non-negative integer');
  }
  return value;
};

const readBudget = async (rli: Interface): Promise<bigint> => {
  const raw = await rli.question('Enter employer maximum budget (public): ');
  const value = BigInt(raw.trim());
  if (value < 0n) {
    throw new Error('Budget must be a non-negative integer');
  }
  return value;
};

/* **********************************************************************
 * deployOrJoinHR: returns an HRAPI instance, by prompting the user about
 * whether to deploy a new contract or join an existing one. The candidate
 * salary is collected first and used as the initial private state either way.
 */

const DEPLOY_OR_JOIN_QUESTION = `
You can do one of the following:
  1. Deploy a new salary verification contract
  2. Join an existing salary verification contract
  3. Exit
Which would you like to do? `;

const deployOrJoinHR = async (providers: HRProviders, rli: Interface, logger: Logger): Promise<HRAPI | null> => {
  const candidateSalary = await readSalary(rli);

  while (true) {
    const choice = await rli.question(DEPLOY_OR_JOIN_QUESTION);
    switch (choice) {
      case '1': {
        const api = await HRAPI.deploy(providers, candidateSalary, logger);
        logger.info(`Deployed contract at address: ${api.deployedContractAddress}`);
        return api;
      }
      case '2': {
        const contractAddress = await rli.question('What is the contract address (in hex)? ');
        const api = await HRAPI.join(providers, contractAddress, candidateSalary, logger);
        logger.info(`Joined contract at address: ${api.deployedContractAddress}`);
        return api;
      }
      case '3':
        logger.info('Exiting...');
        return null;
      default:
        logger.error(`Invalid choice: ${choice}`);
    }
  }
};

/* **********************************************************************
 * displayLedgerState: shows the current `verified` field on the ledger.
 * This never touches private state, so it is always safe to log.
 */

const displayLedgerState = async (
  providers: HRProviders,
  deployedHRContract: DeployedHRContract,
  logger: Logger,
): Promise<void> => {
  const contractAddress = deployedHRContract.deployTxData.public.contractAddress;
  const ledgerState = await getHRLedgerState(providers, contractAddress);
  if (ledgerState === null) {
    logger.info(`There is no HR verification contract deployed at ${contractAddress}`);
  } else {
    logger.info(`Current verified state is: '${ledgerState.verified}'`);
  }
};

/* **********************************************************************
 * displayDerivedState: shows the last-known verified result from the
 * subscribed state observable.
 */

const displayDerivedState = (state: HRDerivedState | undefined, logger: Logger) => {
  if (state === undefined || state.verified === undefined) {
    logger.info('No verification has been run yet');
  } else {
    logger.info(`Current verified state is: '${state.verified}'`);
  }
};

/* **********************************************************************
 * mainLoop: the main interactive menu of the HR verification CLI.
 * Before starting the loop, the user is prompted to deploy a new
 * contract or join an existing one.
 */

const MAIN_LOOP_QUESTION = `
You can do one of the following:
  1. Verify salary against an employer budget
  2. Display the current ledger state (known by everyone)
  3. Display the current derived state (known only to this DApp instance)
  4. Exit
Which would you like to do? `;

const mainLoop = async (providers: HRProviders, rli: Interface, logger: Logger): Promise<void> => {
  const hrApi = await deployOrJoinHR(providers, rli, logger);
  if (hrApi === null) {
    return;
  }
  let currentState: HRDerivedState | undefined;
  const stateObserver = {
    next: (state: HRDerivedState) => (currentState = state),
  };
  const subscription = hrApi.state$.subscribe(stateObserver);
  try {
    while (true) {
      const choice = await rli.question(MAIN_LOOP_QUESTION);
      try {
        switch (choice) {
          case '1': {
            const budget = await readBudget(rli);
            const result = await hrApi.verifySalary(budget);
            // NEVER log the candidate salary here — only the public budget
            // and the disclosed boolean outcome.
            if (result) {
              logger.info(
                `✓ Candidate satisfies salary budget\n  Employer budget: $${budget}\n  Result: VERIFIED`,
              );
            } else {
              logger.info(
                `✗ Candidate does not satisfy salary budget\n  Employer budget: $${budget}\n  Result: NOT VERIFIED`,
              );
            }
            break;
          }
          case '2':
            await displayLedgerState(providers, hrApi.deployedContract, logger);
            break;
          case '3':
            displayDerivedState(currentState, logger);
            break;
          case '4':
            logger.info('Exiting...');
            return;
          default:
            logger.error(`Invalid choice: ${choice}`);
        }
      } catch (e) {
        logError(logger, e);
        logger.info('Returning to main menu...');
      }
    }
  } finally {
    // While we allow errors to bubble up to the 'run' function, we will always need to dispose of the state
    // subscription when we exit.
    subscription.unsubscribe();
  }
};

/* ***********************************************************************
 * This seed gives access to tokens minted in the genesis block of a local development node - only
 * used in standalone networks to build a wallet with initial funds.
 */
const GENESIS_MINT_WALLET_SEED = '0000000000000000000000000000000000000000000000000000000000000001';

/* **********************************************************************
 * buildWallet: unless running in a standalone (offline) mode,
 * prompt the user to tell us whether to create a new wallet
 * or recreate one from a prior seed.
 */

const WALLET_LOOP_QUESTION = `
You can do one of the following:
  1. Build a fresh wallet
  2. Build wallet from a seed
  3. Exit
Which would you like to do? `;

const buildWallet = async (config: Config, rli: Interface, logger: Logger): Promise<string | undefined> => {
  if (config instanceof StandaloneConfig) {
    return GENESIS_MINT_WALLET_SEED;
  }
  while (true) {
    const choice = await rli.question(WALLET_LOOP_QUESTION);
    switch (choice) {
      case '1':
        return toHex(randomBytes(32));
      case '2':
        return await rli.question('Enter your wallet seed: ');
      case '3':
        logger.info('Exiting...');
        return undefined;
      default:
        logger.error(`Invalid choice: ${choice}`);
    }
  }
};

/* **********************************************************************
 * run: the main entry point that starts the whole HR verification CLI.
 *
 * If called with a Docker environment argument, the application
 * will wait for Docker to be ready before doing anything else.
 */

export const run = async (config: Config, testEnv: TestEnvironment, logger: Logger): Promise<void> => {
  const rli = createInterface({ input, output, terminal: true });
  const providersToBeStopped: MidnightWalletProvider[] = [];
  try {
    const envConfiguration = await testEnv.start();
    logger.info(`Environment started with configuration: ${JSON.stringify(envConfiguration)}`);
    const seed = await buildWallet(config, rli, logger);
    if (seed === undefined) {
      return;
    }
    const walletProvider = await MidnightWalletProvider.build(logger, envConfiguration, seed);
    providersToBeStopped.push(walletProvider);
    const walletFacade: WalletFacade = walletProvider.wallet;

    await walletProvider.start();

    const unshieldedState = await waitForUnshieldedFunds(logger, walletFacade, envConfiguration, unshieldedToken());
    const nightBalance = unshieldedState.balances[unshieldedToken().raw];
    if (nightBalance === undefined) {
      logger.info('No funds received, exiting...');
      return;
    }
    logger.info(`Your NIGHT wallet balance is: ${nightBalance}`);

    if (config.generateDust) {
      const dustGeneration = await generateDust(logger, seed, unshieldedState, walletFacade);
      if (dustGeneration) {
        logger.info(`Submitted dust generation registration transaction: ${dustGeneration}`);
        await syncWallet(logger, walletFacade);
      }
    }

    const zkConfigProvider = new NodeZkConfigProvider<'verifySalary'>(config.zkConfigPath);
    const providers: HRProviders = {
      privateStateProvider: levelPrivateStateProvider<PrivateStateId, HRPrivateState>({
        privateStateStoreName: config.privateStateStoreName,
        signingKeyStoreName: `${config.privateStateStoreName}-signing-keys`,
        privateStoragePasswordProvider: () => {
          return 'HR-Verification-Test-2026!';
        },
        accountId: seed,
      }),
      publicDataProvider: indexerPublicDataProvider(envConfiguration.indexer, envConfiguration.indexerWS),
      zkConfigProvider: zkConfigProvider,
      proofProvider: httpClientProofProvider(envConfiguration.proofServer, zkConfigProvider),
      walletProvider: walletProvider,
      midnightProvider: walletProvider,
    };
    await mainLoop(providers, rli, logger);
  } catch (e) {
    logError(logger, e);
    logger.info('Exiting...');
  } finally {
    try {
      rli.close();
      rli.removeAllListeners();
    } catch (e) {
      logError(logger, e);
    } finally {
      try {
        for (const wallet of providersToBeStopped) {
          logger.info('Stopping wallet...');
          await wallet.stop();
        }
        if (testEnv) {
          logger.info('Stopping test environment...');
          await testEnv.shutdown();
        }
      } catch (e) {
        logError(logger, e);
      }
    }
  }
};

function logError(logger: Logger, e: unknown) {
  if (e instanceof Error) {
    logger.error(`Found error '${e.message}'`);
    logger.debug(`${e.stack}`);
  } else {
    logger.error(`Found error (unknown type)`);
  }
}
