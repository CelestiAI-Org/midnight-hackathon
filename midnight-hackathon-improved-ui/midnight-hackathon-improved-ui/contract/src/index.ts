import { CompiledContract } from "@midnight-ntwrk/midnight-js-protocol/compact-js";

export * from "./managed/hr-verification/contract/index.js";
export * from "./witnesses.js";

import * as CompiledHRVerificationContract from "./managed/hr-verification/contract/index.js";
import * as Witnesses from "./witnesses.js";

export const CompiledHRVerificationContractContract = CompiledContract.make<
  CompiledHRVerificationContract.Contract<Witnesses.HRPrivateState>
>(
  "HRVerification",
  CompiledHRVerificationContract.Contract<Witnesses.HRPrivateState>,
).pipe(
  CompiledContract.withWitnesses(Witnesses.witnesses),
  CompiledContract.withCompiledFileAssets("./managed/hr-verification"),
);
