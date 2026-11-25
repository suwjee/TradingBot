# Master specification

Define actual implemented behavior for both directions without inventing trading rules. Full RAW -> aggregation -> chronology -> reaction/reset -> Blue -> A -> S and physical Orders -> E -> lifecycle/StopAll -> Order_B feedback and reconciliation -> primary/reversal -> visibility -> T/F -> serialization. Calculation uses full history before presentation filtering. Preserve exact Decimal representation, ordering, identities and ownership. Do not infer missing logic.

Algorithm families: CU core utilities, DP direction policy, RX reaction/reset, BL Blue, AZ A, SZ S, OA Order audit, EZ E, LC lifecycle/StopAll, PS primary, TF True/False, TB trading bridge, LB live bridge. These identifiers are groups, not evidence of full branch coverage. Physical geometry, calculation eligibility, and final presentation are separate layers. An Order can have an opposite direction to the market.

The explicit contracts in Algorithms/21_RAW_Aggregation_Contract.md, 22_True_False_Exact_Contract.md and 23_Live_Transport_Contract.md refine the earlier summaries. Exact standalone coverage of complex helpers remains incomplete. No unverified section is production-ready. References are supplementary, not a substitute for independent validation.
