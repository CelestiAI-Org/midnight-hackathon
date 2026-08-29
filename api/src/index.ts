import { type ContractAddress } from '@midnight-ntwrk/midnight-js-protocol/compact-runtime';
import { type Logger } from 'pino';
import {
  type HRDerivedState,
  type HRContract,
  type HRProviders,
  type DeployedHRContract,
  hrPrivateStateKey,
} from './common-types.js';
import { ledger, CompiledHRVerificationContractContract } from '../../contract/src/index';
import { HRPrivateState, createHRPrivateState } from '../../contract/src/witnesses.js';
import { deployContract, findDeployedContract } from '@midnight-ntwrk/midnight-js-contracts';
import { map, type Observable } from 'rxjs';

export interface DeployedHRAPI {
  readonly deployedContractAddress: ContractAddress;
  readonly state$: Observable<HRDerivedState>;
  verifySalary: (budget: bigint) => Promise<boolean>;
}

export class HRAPI implements DeployedHRAPI {
  private constructor(
    public readonly deployedContract: DeployedHRContract,
    private readonly providers: HRProviders,
    private readonly logger?: Logger,
  ) {
    this.deployedContractAddress = deployedContract.deployTxData.public.contractAddress;
    providers.privateStateProvider.setContractAddress(this.deployedContractAddress);

    this.state$ = providers.publicDataProvider
      .contractStateObservable(this.deployedContractAddress, { type: 'latest' })
      .pipe(map((contractState) => ({ verified: ledger(contractState.data).verified })));
  }

  readonly deployedContractAddress: ContractAddress;
  readonly state$: Observable<HRDerivedState>;

  async verifySalary(budget: bigint): Promise<boolean> {
    this.logger?.info(`verifyingSalary against budget: ${budget}`);
    const txData = await this.deployedContract.callTx.verifySalary(budget);
    this.logger?.trace({
      transactionAdded: {
        circuit: 'verifySalary',
        txHash: txData.public.txHash,
        blockHeight: txData.public.blockHeight,
      },
    });
    const contractState = await this.providers.publicDataProvider.queryContractState(this.deployedContractAddress);
    if (contractState === null) {
      throw new Error('Contract state not found after verifySalary transaction');
    }
    return ledger(contractState.data).verified;
  }

  static async deploy(providers: HRProviders, candidateSalary: bigint, logger?: Logger): Promise<HRAPI> {
    logger?.info('deployContract');
    const deployedContract = await deployContract(providers, {
      compiledContract: CompiledHRVerificationContractContract,
      privateStateId: hrPrivateStateKey,
      initialPrivateState: createHRPrivateState(candidateSalary),
    });
    return new HRAPI(deployedContract, providers, logger);
  }

  static async join(
    providers: HRProviders,
    contractAddress: ContractAddress,
    candidateSalary: bigint,
    logger?: Logger,
  ): Promise<HRAPI> {
    logger?.info({ joinContract: { contractAddress } });
    const deployedContract = await findDeployedContract<HRContract>(providers, {
      contractAddress,
      compiledContract: CompiledHRVerificationContractContract,
      privateStateId: hrPrivateStateKey,
      initialPrivateState: createHRPrivateState(candidateSalary),
    });
    return new HRAPI(deployedContract, providers, logger);
  }
}

export * from './common-types.js';
