# Buddy Native Bot Coverage

Buddy should try repository-native bot code first. Optional models are backup helpers, not the default owner of the task.

## Summary

- Python bot/agent files scanned: 1920
- Native runnable candidates: 1292
- Partial native implementations: 350
- Needs native completion: 278
- Native task routes: 16

## Native Task Routes

- `business_building` -> `RetailTradeBot` at `Business_bots/retail_trade_bot.py` (ready_candidate, 338 candidates)
- `coding` -> `UniversalCodingLibraryBot` at `bots/universal_coding_library_bot/bot.py` (ready_candidate, 371 candidates)
- `creative_media` -> `CineCoreBot` at `bots/cinecore_bot/cinecore_bot.py` (ready_candidate, 183 candidates)
- `customer_support` -> `CustomerSupportBot` at `bots/customer_support_bot/bot.py` (partial, 295 candidates)
- `data_and_research` -> `GovernmentContractGrantBot` at `bots/government-contract-grant-bot/government_contract_grant_bot.py` (ready_candidate, 1469 candidates)
- `education` -> `EducationLibraryBot` at `Occupational_bots/education_library_bot.py` (ready_candidate, 144 candidates)
- `finance` -> `FinanceBot` at `bots/finance-bot/finance_bot.py` (ready_candidate, 363 candidates)
- `games_and_simulations` -> `FinancialLiteracyBot` at `bots/financial_literacy_bot/financial_literacy_bot.py` (ready_candidate, 162 candidates)
- `general_automation` -> `LifestyleBot` at `bots/lifestyle_bot/lifestyle_bot.py` (ready_candidate, 15 candidates)
- `health_and_care` -> `HealthWellnessBot` at `bots/health_wellness_bot/health_wellness_bot.py` (ready_candidate, 158 candidates)
- `legal_and_compliance` -> `GovernmentContractGrantBot` at `bots/government-contract-grant-bot/government_contract_grant_bot.py` (ready_candidate, 468 candidates)
- `marketing` -> `MarketingBot` at `bots/marketing-bot/marketing_bot.py` (ready_candidate, 642 candidates)
- `operations` -> `TransportationWarehousingBot` at `Business_bots/transportation_warehousing_bot.py` (ready_candidate, 382 candidates)
- `real_estate` -> `RealEstateLeasingBot` at `Business_bots/real_estate_leasing_bot.py` (ready_candidate, 131 candidates)
- `sales_and_leads` -> `SalesBot` at `Occupational_bots/sales_bot.py` (ready_candidate, 210 candidates)
- `security` -> `ComputerMathBot` at `Occupational_bots/computer_math_bot.py` (ready_candidate, 139 candidates)

## Operating Rule

Buddy should only ask an optional model/resource after native code has been checked, when the user chooses model help, or when a capability is not yet fully implemented locally.
