import { Ledger } from "./managed/hr-verification/contract/index.js";
import { WitnessContext } from "@midnight-ntwrk/midnight-js-protocol/compact-runtime";

export type HRPrivateState = {
  readonly candidateSalary: bigint;
};

export const createHRPrivateState = (
  candidateSalary: bigint,
): HRPrivateState => ({
  candidateSalary,
});

export const witnesses = {
  candidateSalary: ({
    privateState,
  }: WitnessContext<Ledger, HRPrivateState>): [
    HRPrivateState,
    bigint,
  ] => [privateState, privateState.candidateSalary],
};
