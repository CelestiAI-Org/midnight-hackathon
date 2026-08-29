// hr-cli/src/server.ts
//
// Minimal HTTP wrapper around HRAPI for the Streamlit demo frontend.
// Boots the same wallet/proof-server/provider stack as the interactive CLI
// (see index.ts run()), but instead of a readline loop, exposes:
//
//   GET  /health
//   POST /verify   { candidateId: number, budget: number } -> { verified, contractAddress, txHash }
//
// The candidate's salary is looked up server-side from CANDIDATE_SALARIES
// below and is NEVER included in a request or response body. Streamlit only
// ever sends a candidateId and a public budget.

import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import { WebSocket } from 'ws';
import { HRAPI, type HRProviders, type PrivateStateId } from '../../api/src/index';
import { NodeZkConfigProvider } from '@midnight-ntwrk/midnight-js-node-zk-config-provider';
import { indexerPublicDataProvider } from '@midnight-ntwrk/midnight-js-indexer-public-data-provider';
import { httpClientProofProvider } from '@midnight-ntwrk/midnight-js-http-client-proof-provider';
import { levelPrivateStateProvider } from '@midnight-ntwrk/midnight-js-level-private-state-provider';
import { StandaloneConfig } from './config.js';
import { MidnightWalletProvider } from './midnight-wallet-provider';
import { unshieldedToken } from '@midnight-ntwrk/midnight-js-protocol/ledger';
import { waitForUnshieldedFunds } from './wallet-utils';
import { HRPrivateState } from '../../contract/src/witnesses.js';
import { createLogger } from './logger-utils.js';

// @ts-expect-error: needed for WebSocket usage through apollo
globalThis.WebSocket = WebSocket;

const PORT = 4000;

// Server-side only. Mirrors the mock candidate list's salary_expectation
// values in app.py. In a real deployment this would come from a database
// the browser/Streamlit process never has access to.
const CANDIDATE_SALARIES: Record<number, bigint> = {
  1: 88000n,
  2: 72000n,
  3: 67000n,
  4: 91000n,
  5: 62000n,
  6: 90000n,
  7: 110000n,
  8: 70000n,
  9: 58000n,
};

const GENESIS_MINT_WALLET_SEED = '0000000000000000000000000000000000000000000000000000000000000001';

// Cache one deployed contract per candidate so repeated verifications
// (e.g. re-clicking "Verify" in the demo) don't redeploy every time.
const deployedByCandidate = new Map<number, HRAPI>();

async function readJsonBody(req: IncomingMessage): Promise<any> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) chunks.push(chunk as Buffer);
  const raw = Buffer.concat(chunks).toString('utf-8');
  return raw ? JSON.parse(raw) : {};
}

function sendJson(res: ServerResponse, status: number, body: unknown) {
  const payload = JSON.stringify(body);
  res.writeHead(status, { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(payload) });
  res.end(payload);
}

async function main() {
  const config = new StandaloneConfig();
  const logger = await createLogger(config.logDir);
  const testEnv = config.getEnvironment(logger);

  const envConfiguration = await testEnv.start();
  logger.info(`Environment started: ${JSON.stringify(envConfiguration)}`);

  const walletProvider = await MidnightWalletProvider.build(logger, envConfiguration, GENESIS_MINT_WALLET_SEED);
  await walletProvider.start();

  const unshieldedState = await waitForUnshieldedFunds(logger, walletProvider.wallet, envConfiguration, unshieldedToken());
  const nightBalance = unshieldedState.balances[unshieldedToken().raw];
  logger.info(`Service wallet NIGHT balance: ${nightBalance}`);
  if (nightBalance === undefined || nightBalance === 0n) {
    throw new Error('Service wallet received no funds — cannot proceed.');
  }

  const zkConfigProvider = new NodeZkConfigProvider<'verifySalary'>(config.zkConfigPath);
  const providers: HRProviders = {
    privateStateProvider: levelPrivateStateProvider<PrivateStateId, HRPrivateState>({
      privateStateStoreName: config.privateStateStoreName,
      signingKeyStoreName: `${config.privateStateStoreName}-signing-keys`,
      privateStoragePasswordProvider: () => 'HR-Verification-Test-2026!',
      accountId: GENESIS_MINT_WALLET_SEED,
    }),
    publicDataProvider: indexerPublicDataProvider(envConfiguration.indexer, envConfiguration.indexerWS),
    zkConfigProvider,
    proofProvider: httpClientProofProvider(envConfiguration.proofServer, zkConfigProvider),
    walletProvider,
    midnightProvider: walletProvider,
  };

  const server = createServer(async (req, res) => {
    try {
      if (req.method === 'GET' && req.url === '/health') {
        sendJson(res, 200, { ok: true });
        return;
      }

      if (req.method === 'POST' && req.url === '/verify') {
        const body = await readJsonBody(req);
        const candidateId = Number(body.candidateId);
        const budget = BigInt(body.budget);

        const salary = CANDIDATE_SALARIES[candidateId];
        if (salary === undefined) {
          sendJson(res, 404, { error: `Unknown candidateId: ${candidateId}` });
          return;
        }

        logger.info(`verify request: candidateId=${candidateId} budget=${budget}`);
        // NOTE: intentionally never logging `salary` here.

        let api = deployedByCandidate.get(candidateId);
        if (!api) {
          api = await HRAPI.deploy(providers, salary, logger);
          deployedByCandidate.set(candidateId, api);
          logger.info(`deployed contract for candidateId=${candidateId} at ${api.deployedContractAddress}`);
        }

        const verified = await api.verifySalary(budget);
        sendJson(res, 200, {
          verified,
          contractAddress: api.deployedContractAddress,
        });
        return;
      }

      sendJson(res, 404, { error: 'Not found' });
    } catch (e) {
      logger.error(e instanceof Error ? e.message : 'unknown error');
      sendJson(res, 500, { error: e instanceof Error ? e.message : 'internal error' });
    }
  });

  server.listen(PORT, () => {
    logger.info(`HR verification service listening on http://localhost:${PORT}`);
  });
}

main().catch((e) => {
  console.error('Fatal error starting HR verification service:', e);
  process.exit(1);
});
