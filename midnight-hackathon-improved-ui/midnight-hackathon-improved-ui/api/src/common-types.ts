import { type MidnightProviders } from '@midnight-ntwrk/midnight-js-types';
import { type FoundContract } from '@midnight-ntwrk/midnight-js-contracts';
import type { Ledger, Contract, Witnesses } from '../../contract/src/index';
import type { HRPrivateState } from '../../contract/src/witnesses';

export const hrPrivateStateKey = 'hrPrivateState';
export type PrivateStateId = typeof hrPrivateStateKey;

export type PrivateStates = {
  readonly hrPrivateState: HRPrivateState;
};

export type HRContract = Contract<HRPrivateState, Witnesses<HRPrivateState>>;

export type HRCircuitKeys = Exclude<keyof HRContract['impureCircuits'], number | symbol>;

export type HRProviders = MidnightProviders<HRCircuitKeys, PrivateStateId, HRPrivateState>;

export type DeployedHRContract = FoundContract<HRContract>;

export type HRDerivedState = {
  readonly verified: boolean | undefined;
};
