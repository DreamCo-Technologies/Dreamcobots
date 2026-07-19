import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import {
  Banknote, Building2, Calculator, Car, CheckCircle2, Clock, Copy,
  CreditCard, DollarSign, ExternalLink, Gift, GraduationCap, Hammer,
  Landmark, Percent, Search, ShieldCheck, Sparkles, Star, Tag, Target,
  TrendingUp, Trophy, Truck, Users, Wallet, Zap,
} from "lucide-react";

// ── LOANS ──────────────────────────────────────────────────────────────────
const LOAN_OFFERS = [
  { id: 1, lender: "SBA 7(a) Program", type: "SBA", apr: 10.5, minAmount: 5000, maxAmount: 5000000, termMonths: 84, monthlyPayment: 0, approval: "medium" as const, icon: ShieldCheck, url: "https://sba.gov/funding-programs/loans/7a-loans", note: "Backed by US govt" },
  { id: 2, lender: "SBA Microloan", type: "SBA", apr: 8.0, minAmount: 500, maxAmount: 50000, termMonths: 72, monthlyPayment: 0, approval: "high" as const, icon: ShieldCheck, url: "https://sba.gov/funding-programs/loans/microloans", note: "For startups & nonprofits" },
  { id: 3, lender: "BlueVine", type: "Business Line", apr: 6.2, minAmount: 5000, maxAmount: 250000, termMonths: 12, monthlyPayment: 0, approval: "high" as const, icon: Building2, url: "https://bluevine.com", note: "Fast approval, 1-3 days" },
  { id: 4, lender: "Kabbage (AmEx)", type: "Business Line", apr: 9.0, minAmount: 2000, maxAmount: 250000, termMonths: 18, monthlyPayment: 0, approval: "high" as const, icon: Building2, url: "https://kabbage.com", note: "Instant approval possible" },
  { id: 5, lender: "Fundbox", type: "Business Line", apr: 4.66, minAmount: 1000, maxAmount: 150000, termMonths: 12, monthlyPayment: 0, approval: "high" as const, icon: Zap, url: "https://fundbox.com", note: "Same-day funding" },
  { id: 6, lender: "OnDeck", type: "Term Loan", apr: 29.9, minAmount: 5000, maxAmount: 250000, termMonths: 24, monthlyPayment: 0, approval: "high" as const, icon: Wallet, url: "https://ondeck.com", note: "Bad credit OK" },
  { id: 7, lender: "LendingClub Business", type: "Term Loan", apr: 8.05, minAmount: 5000, maxAmount: 500000, termMonths: 60, monthlyPayment: 0, approval: "medium" as const, icon: Users, url: "https://lendingclub.com/business", note: "Fixed rate loans" },
  { id: 8, lender: "Kiva (0% micro)", type: "Microloan", apr: 0.0, minAmount: 1000, maxAmount: 15000, termMonths: 36, monthlyPayment: 0, approval: "high" as const, icon: Sparkles, url: "https://kiva.org/borrow", note: "0% interest — crowdfunded" },
  { id: 9, lender: "National Funding", type: "Equipment", apr: 8.0, minAmount: 10000, maxAmount: 500000, termMonths: 60, monthlyPayment: 0, approval: "medium" as const, icon: Hammer, url: "https://nationalfunding.com", note: "Equipment & working capital" },
  { id: 10, lender: "PayPal Business Loan", type: "Term Loan", apr: 12.0, minAmount: 1000, maxAmount: 150000, termMonths: 24, monthlyPayment: 0, approval: "high" as const, icon: DollarSign, url: "https://paypal.com/us/business/business-loans", note: "Tied to PayPal sales" },
  { id: 11, lender: "Shopify Capital", type: "Revenue-Based", apr: 0, minAmount: 200, maxAmount: 2000000, termMonths: 0, monthlyPayment: 0, approval: "high" as const, icon: TrendingUp, url: "https://shopify.com/capital", note: "Revenue share, no fixed term" },
  { id: 12, lender: "Square Loans", type: "Revenue-Based", apr: 0, minAmount: 300, maxAmount: 250000, termMonths: 0, monthlyPayment: 0, approval: "high" as const, icon: TrendingUp, url: "https://squareup.com/us/en/loans", note: "Based on Square volume" },
  { id: 13, lender: "Credibly", type: "Working Capital", apr: 9.99, minAmount: 5000, maxAmount: 400000, termMonths: 24, monthlyPayment: 0, approval: "medium" as const, icon: Landmark, url: "https://credibly.com", note: "Bad credit considered" },
  { id: 14, lender: "Lendio (Marketplace)", type: "Marketplace", apr: 3.0, minAmount: 500, maxAmount: 5000000, termMonths: 300, monthlyPayment: 0, approval: "high" as const, icon: Search, url: "https://lendio.com", note: "Compares 75+ lenders" },
  { id: 15, lender: "Accion Opportunity Fund", type: "Community", apr: 8.49, minAmount: 300, maxAmount: 100000, termMonths: 60, monthlyPayment: 0, approval: "high" as const, icon: Users, url: "https://accionopportunityfund.org", note: "Underserved entrepreneurs" },
  { id: 16, lender: "IBank (CA)", type: "State", apr: 5.5, minAmount: 500, maxAmount: 100000, termMonths: 60, monthlyPayment: 0, approval: "medium" as const, icon: Landmark, url: "https://ibank.ca.gov", note: "California small biz" },
  { id: 17, lender: "Nav (Marketplace)", type: "Marketplace", apr: 0, minAmount: 1000, maxAmount: 5000000, termMonths: 0, monthlyPayment: 0, approval: "high" as const, icon: Search, url: "https://nav.com", note: "Matches based on credit profile" },
  { id: 18, lender: "Greenbox Capital", type: "MCA", apr: 0, minAmount: 3000, maxAmount: 500000, termMonths: 18, monthlyPayment: 0, approval: "high" as const, icon: Zap, url: "https://greenboxcapital.com", note: "Merchant cash advance" },
  { id: 19, lender: "QuarterSpot", type: "Term Loan", apr: 25.0, minAmount: 5000, maxAmount: 150000, termMonths: 18, monthlyPayment: 0, approval: "high" as const, icon: Clock, url: "https://quarterspot.com", note: "6-month revenue history" },
  { id: 20, lender: "USDA Business Loan", type: "Government", apr: 5.75, minAmount: 100000, maxAmount: 25000000, termMonths: 300, monthlyPayment: 0, approval: "low" as const, icon: ShieldCheck, url: "https://rd.usda.gov/programs-services/business-programs", note: "Rural business focus" },
];

// ── CREDIT CARDS ────────────────────────────────────────────────────────────
const CREDIT_CARDS = [
  { id: 1, name: "Chase Ink Business Cash", issuer: "Chase", reward: "5% cash back (office/telecom)", annualFee: 0, creditLine: "$75,000+", apr: "18.49%", bonus: "$750 (after $6k spend)", category: "Cash Back", url: "https://creditcards.chase.com/business-credit-cards/ink/cash" },
  { id: 2, name: "Ink Business Unlimited", issuer: "Chase", reward: "1.5% unlimited cash back", annualFee: 0, creditLine: "$75,000+", apr: "18.49%", bonus: "$750 (after $6k spend)", category: "Cash Back", url: "https://creditcards.chase.com/business-credit-cards/ink/unlimited" },
  { id: 3, name: "AmEx Business Gold", issuer: "American Express", reward: "4x on top 2 spend categories", annualFee: 375, creditLine: "Flexible", apr: "N/A (charge)", bonus: "100,000 MR pts", category: "Travel/Rewards", url: "https://americanexpress.com/en-us/business/credit-cards/business-gold" },
  { id: 4, name: "AmEx Business Platinum", issuer: "American Express", reward: "5x flights/hotels; 1.5x $5k+", annualFee: 695, creditLine: "Flexible", apr: "N/A (charge)", bonus: "150,000 MR pts", category: "Premium Travel", url: "https://americanexpress.com/en-us/business/credit-cards/business-platinum" },
  { id: 5, name: "Capital One Spark Cash Plus", issuer: "Capital One", reward: "2% cash back everywhere", annualFee: 150, creditLine: "Flexible", apr: "N/A (charge)", bonus: "$1,200 (after $30k spend)", category: "Cash Back", url: "https://capitalone.com/small-business/credit-cards/spark-cash-plus" },
  { id: 6, name: "Capital One Spark Miles", issuer: "Capital One", reward: "2x miles everywhere", annualFee: 95, creditLine: "Flexible", apr: "26.24%", bonus: "50,000 miles", category: "Travel", url: "https://capitalone.com/small-business/credit-cards/spark-miles" },
  { id: 7, name: "Bank of America Business Adv.", issuer: "Bank of America", reward: "3% chosen category, 2% dining", annualFee: 0, creditLine: "$50,000+", apr: "17.99%", bonus: "$300 (after $3k spend)", category: "Cash Back", url: "https://bankofamerica.com/smallbusiness/credit-cards" },
  { id: 8, name: "Brex Corporate Card", issuer: "Brex", reward: "7x rideshare, 4x travel, 3x food", annualFee: 0, creditLine: "Based on deposits", apr: "N/A", bonus: "50,000 pts (after $9k spend)", category: "Startup", url: "https://brex.com/product/credit-card" },
  { id: 9, name: "Ramp Corporate Card", issuer: "Ramp", reward: "1.5% unlimited cash back", annualFee: 0, creditLine: "Based on deposits", apr: "N/A", bonus: "$250 (partners)", category: "Cost Control", url: "https://ramp.com" },
  { id: 10, name: "Divvy Business Card", issuer: "Divvy/BILL", reward: "7x hotels, 5x restaurants", annualFee: 0, creditLine: "Weekly limit", apr: "N/A", bonus: "Various", category: "Expense Mgmt", url: "https://divvy.com" },
  { id: 11, name: "US Bank Business Triple Cash", issuer: "US Bank", reward: "3% gas/office/restaurants/phone", annualFee: 0, creditLine: "$25,000+", apr: "19.24%", bonus: "$500 (after $4,500 spend)", category: "Cash Back", url: "https://usbank.com/credit-cards/business" },
  { id: 12, name: "Costco Anywhere Visa Business", issuer: "Citi", reward: "4% gas, 3% restaurants, 2% Costco", annualFee: 0, creditLine: "Varies", apr: "20.24%", bonus: "None", category: "Warehouse", url: "https://citicards.com" },
  { id: 13, name: "Stripe Corporate Card", issuer: "Stripe", reward: "1.5% cash back on all spend", annualFee: 0, creditLine: "Based on Stripe revenue", apr: "N/A", bonus: "Various credits", category: "Fintech", url: "https://stripe.com/corporate-card" },
  { id: 14, name: "Sam's Club Business MC", issuer: "Synchrony", reward: "5% Sam's fuel, 3% dining", annualFee: 0, creditLine: "Varies", apr: "21.15%", bonus: "$30 statement credit", category: "Warehouse", url: "https://creditcard.samsclub.com" },
  { id: 15, name: "Wells Fargo Business Elite", issuer: "Wells Fargo", reward: "1.5% cash back or 1 pt/dollar", annualFee: 125, creditLine: "$100,000+", apr: "Prime + 7.99%", bonus: "$1,000 (after $25k spend)", category: "Premium", url: "https://wellsfargo.com/biz/credit-cards" },
];

// ── INVESTORS ──────────────────────────────────────────────────────────────
const INVESTORS = [
  { id: 1, name: "Y Combinator", type: "Accelerator", stage: "Pre-seed / Seed", check: "$500K", focus: "Any sector", url: "https://ycombinator.com/apply", acceptance: "~2%", note: "2× / year batches" },
  { id: 2, name: "Andreessen Horowitz (a16z)", type: "VC", stage: "Seed → Growth", check: "$1M–$500M", focus: "AI, Crypto, SaaS, Bio", url: "https://a16z.com", acceptance: "<1%", note: "Top-tier; need intro" },
  { id: 3, name: "Sequoia Capital", type: "VC", stage: "Seed → IPO", check: "$1M–$1B", focus: "Tech, AI, Consumer", url: "https://sequoiacap.com", acceptance: "<1%", note: "Arc seed program" },
  { id: 4, name: "Techstars", type: "Accelerator", stage: "Pre-seed", check: "$120K", focus: "Any", url: "https://techstars.com/apply", acceptance: "~1%", note: "Worldwide locations" },
  { id: 5, name: "AngelList", type: "Angel Network", stage: "Pre-seed / Seed", check: "$50K–$500K", focus: "Tech startups", url: "https://venture.angellist.com", acceptance: "Variable", note: "Rolling Funds available" },
  { id: 6, name: "500 Global", type: "VC + Accelerator", stage: "Pre-seed / Seed", check: "$150K+", focus: "Global tech", url: "https://500.co", acceptance: "~3%", note: "Global reach, 80+ countries" },
  { id: 7, name: "First Round Capital", type: "VC", stage: "Seed", check: "$500K–$3M", focus: "B2B SaaS, Consumer", url: "https://firstround.com", acceptance: "<1%", note: "Known for community" },
  { id: 8, name: "SoftBank Vision Fund", type: "VC", stage: "Growth / Late", check: "$100M+", focus: "AI, Tech mega-rounds", url: "https://visionfund.com", acceptance: "<0.5%", note: "Largest VC fund ever" },
  { id: 9, name: "Tiger Global", type: "VC / PE", stage: "Series A → Growth", check: "$5M–$500M", focus: "Tech, SaaS", url: "https://tigerglobal.com", acceptance: "Invite only", note: "Fast decisions" },
  { id: 10, name: "Kleiner Perkins", type: "VC", stage: "Seed → Growth", check: "$1M–$100M", focus: "AI, Climate, Health", url: "https://kleinerperkins.com", acceptance: "<1%", note: "Iconic Silicon Valley fund" },
  { id: 11, name: "Khosla Ventures", type: "VC", stage: "Seed → Growth", check: "$500K–$50M", focus: "DeepTech, AI, Energy", url: "https://khoslaventures.com", acceptance: "<1%", note: "High risk, high impact" },
  { id: 12, name: "General Catalyst", type: "VC", stage: "Seed → IPO", check: "$1M–$250M", focus: "Health, AI, Climate", url: "https://generalcatalyst.com", acceptance: "<1%", note: "Endurance Investing" },
  { id: 13, name: "Founders Fund", type: "VC", stage: "Seed → Growth", check: "$500K–$100M", focus: "Science, AI, Defense", url: "https://foundersfund.com", acceptance: "Invite only", note: "Peter Thiel's fund" },
  { id: 14, name: "Accel", type: "VC", stage: "Seed → Growth", check: "$1M–$100M", focus: "SaaS, Security, AI", url: "https://accel.com", acceptance: "<1%", note: "Global: US, India, Europe" },
  { id: 15, name: "Benchmark", type: "VC", stage: "Series A", check: "$5M–$25M", focus: "Marketplace, SaaS", url: "https://benchmark.com", acceptance: "<0.5%", note: "Small fund, big winners" },
  { id: 16, name: "NEA", type: "VC", stage: "Seed → Late", check: "$1M–$100M", focus: "Tech, Health, Energy", url: "https://nea.com", acceptance: "<1%", note: "One of oldest VCs" },
  { id: 17, name: "Lightspeed", type: "VC", stage: "Seed → Growth", check: "$500K–$200M", focus: "Consumer, Enterprise, Fintech", url: "https://lsvp.com", acceptance: "<1%", note: "Global multi-stage" },
  { id: 18, name: "a16z Speedrun", type: "Accelerator", stage: "Pre-seed", check: "$750K", focus: "AI, Web3", url: "https://a16z.com/speedrun", acceptance: "~3%", note: "8-week virtual program" },
  { id: 19, name: "Plug and Play Tech Center", type: "Accelerator", stage: "Pre-seed / Seed", check: "Up to $250K", focus: "Any vertical", url: "https://plugandplaytechcenter.com", acceptance: "~3%", note: "300+ startups / yr" },
  { id: 20, name: "MassChallenge", type: "Accelerator", stage: "Any", check: "$0–$100K (equity-free)", focus: "Any", url: "https://masschallenge.org", acceptance: "~10%", note: "No equity taken" },
];

// ── GRANTS ──────────────────────────────────────────────────────────────────
const GRANTS = [
  { id: 1, name: "SBIR Phase I", agency: "NSF / SBA / NIH / DoD", amount: "$50K–$275K", deadline: "Rolling (by agency)", eligibility: "US small biz with R&D focus", url: "https://sbir.gov", category: "Government", equity: false },
  { id: 2, name: "STTR Program", agency: "NSF / DoE / DoD", amount: "$150K–$1M", deadline: "Rolling", eligibility: "Small biz + research institution", url: "https://sbir.gov/about/about-sttr", category: "Government", equity: false },
  { id: 3, name: "FedEx Small Business Grant", agency: "FedEx", amount: "$30,000 (grand prize)", deadline: "Annual (Spring)", eligibility: "US small businesses", url: "https://fedex.com/en-us/small-business/grant-contest.html", category: "Corporate", equity: false },
  { id: 4, name: "Amber Grant for Women", agency: "WomensNet", amount: "$30,000 / month", deadline: "Monthly", eligibility: "Women-owned businesses", url: "https://ambergrantsforwomen.com", category: "Women", equity: false },
  { id: 5, name: "IFundWomen Universal Grant", agency: "IFundWomen", amount: "Varies ($500–$25K)", deadline: "Rolling", eligibility: "Women entrepreneurs", url: "https://ifundwomen.com/grants", category: "Women", equity: false },
  { id: 6, name: "Hello Alice Small Business Grant", agency: "Hello Alice", amount: "$25,000", deadline: "Quarterly", eligibility: "US small businesses", url: "https://helloalice.com/grants", category: "Small Biz", equity: false },
  { id: 7, name: "Comcast RISE Grant", agency: "Comcast", amount: "$10,000 + tech/marketing", deadline: "Quarterly", eligibility: "Minority-owned small biz", url: "https://comcastrise.com", category: "Minority", equity: false },
  { id: 8, name: "USDA Value-Added Producer Grant", agency: "USDA", amount: "Up to $250,000", deadline: "Annual (Jan-Feb)", eligibility: "Agricultural producers", url: "https://rd.usda.gov/programs-services/business-programs/value-added-producer-grants", category: "Agriculture", equity: false },
  { id: 9, name: "Visa Everywhere Initiative", agency: "Visa", amount: "$100,000", deadline: "Annual", eligibility: "Fintech startups", url: "https://visaeverywhere.co", category: "Fintech", equity: false },
  { id: 10, name: "HUD Community Dev. Block Grant", agency: "HUD", amount: "Varies (local)", deadline: "Through local govts", eligibility: "Community development projects", url: "https://hud.gov/program_offices/comm_planning/cdbg", category: "Government", equity: false },
  { id: 11, name: "DoE Clean Energy Grant", agency: "Dept of Energy", amount: "$50K–$5M", deadline: "Rolling by topic", eligibility: "Clean/renewable energy biz", url: "https://energy.gov/funding", category: "Energy", equity: false },
  { id: 12, name: "National Science Foundation Grant", agency: "NSF", amount: "$150K–$2M", deadline: "Rolling", eligibility: "Research & innovation", url: "https://nsf.gov/funding", category: "Research", equity: false },
  { id: 13, name: "Google for Startups Accelerator", agency: "Google", amount: "Cloud credits + $0 equity", deadline: "Rolling", eligibility: "AI-first startups (US)", url: "https://startup.google.com/programs/accelerator", category: "Tech", equity: false },
  { id: 14, name: "Microsoft for Startups Founders Hub", agency: "Microsoft", amount: "Up to $350K Azure credits", deadline: "Rolling", eligibility: "Any startup", url: "https://foundershub.startups.microsoft.com", category: "Tech", equity: false },
  { id: 15, name: "AWS Activate", agency: "Amazon", amount: "Up to $100K AWS credits", deadline: "Rolling", eligibility: "Startups (registered)", url: "https://aws.amazon.com/activate", category: "Tech", equity: false },
  { id: 16, name: "Stripe Atlas Grant", agency: "Stripe", amount: "$500 + perks", deadline: "Rolling", eligibility: "New Stripe Atlas companies", url: "https://stripe.com/atlas", category: "Fintech", equity: false },
  { id: 17, name: "Second Chance Business Coalition", agency: "Fortune 500 coalition", amount: "Training + grants", deadline: "Rolling", eligibility: "Justice-involved entrepreneurs", url: "https://secondchancebusiness.org", category: "Reentry", equity: false },
  { id: 18, name: "Tory Burch Foundation Fellowship", agency: "Tory Burch Foundation", amount: "$5,000 + mentorship", deadline: "Annual (Fall)", eligibility: "Women entrepreneurs", url: "https://toryburchfoundation.org/fellowship", category: "Women", equity: false },
  { id: 19, name: "Nav's Business Grant", agency: "Nav", amount: "$10,000", deadline: "Quarterly", eligibility: "US small businesses", url: "https://nav.com/business-grant", category: "Small Biz", equity: false },
  { id: 20, name: "PitchBLACK Competition", agency: "Various Black Biz Orgs", amount: "$10K–$50K", deadline: "Annual", eligibility: "Black-owned businesses", url: "https://pitchblack.us", category: "Minority", equity: false },
];

// ── CONTRACTS ──────────────────────────────────────────────────────────────
const CONTRACTS = [
  { id: 1, name: "SAM.gov (Federal)", platform: "US Government", type: "Federal Contract", value: "$1K–$100M+", eligibility: "US businesses, registered on SAM", url: "https://sam.gov", category: "Government", note: "Mandatory for federal contracts" },
  { id: 2, name: "GSA Schedule", platform: "GSA", type: "Multi-Agency Contract", value: "$25K–$10M+", eligibility: "Established US businesses", url: "https://gsa.gov/buy-through-us/purchasing-programs/gsa-multiple-award-schedule", category: "Government", note: "Pre-negotiated pricing" },
  { id: 3, name: "8(a) Business Development", platform: "SBA", type: "Set-Aside Contract", value: "Varies", eligibility: "Disadvantaged small businesses", url: "https://sba.gov/federal-contracting/contracting-assistance-programs/8a-business-development-program", category: "Government", note: "Sole-source up to $4.5M" },
  { id: 4, name: "HUBZone Program", platform: "SBA", type: "Set-Aside Contract", value: "Varies", eligibility: "HUBZone-located businesses", url: "https://sba.gov/federal-contracting/contracting-assistance-programs/hubzone-program", category: "Government", note: "10% price evaluation preference" },
  { id: 5, name: "WOSB Federal Contracting", platform: "SBA", type: "Set-Aside Contract", value: "Varies", eligibility: "Women-owned small businesses", url: "https://sba.gov/federal-contracting/contracting-assistance-programs/women-owned-small-business-federal-contracting-program", category: "Women", note: "EDWOSB = economically disadvantaged" },
  { id: 6, name: "SDVOSB Contracts", platform: "SBA / VA", type: "Set-Aside Contract", value: "Varies", eligibility: "Service-disabled veteran-owned", url: "https://sba.gov/federal-contracting/contracting-assistance-programs/service-disabled-veteran-owned-businesses", category: "Veterans", note: "VA sole-source authority" },
  { id: 7, name: "Upwork Enterprise", platform: "Upwork", type: "Freelance Contract", value: "$500–$1M+", eligibility: "Any business", url: "https://upwork.com/enterprise", category: "Freelance", note: "Vetted talent pools" },
  { id: 8, name: "Fiverr Business", platform: "Fiverr", type: "Service Contract", value: "$5–$50K", eligibility: "Any business", url: "https://business.fiverr.com", category: "Freelance", note: "Quick turnaround services" },
  { id: 9, name: "Toptal Network", platform: "Toptal", type: "Expert Contract", value: "$50–$200/hr", eligibility: "Any business (screening)", url: "https://toptal.com", category: "Tech Talent", note: "Top 3% developers" },
  { id: 10, name: "Catalant (Expert Marketplace)", platform: "Catalant", type: "Consulting Contract", value: "$5K–$500K", eligibility: "Enterprise clients", url: "https://gocatalant.com", category: "Consulting", note: "Ex-McKinsey / ex-Bain talent" },
  { id: 11, name: "IRS VITA Grant", platform: "IRS", type: "Gov Grant/Contract", value: "Up to $35K", eligibility: "Tax-prep nonprofits/orgs", url: "https://irs.gov/individuals/free-tax-return-preparation-for-qualifying-taxpayers", category: "Finance", note: "Free tax prep partnerships" },
  { id: 12, name: "State DoT Contracts", platform: "State Govts", type: "Infrastructure Contract", value: "$10K–$50M+", eligibility: "Licensed contractors", url: "https://artba.org/business-resources/government-contracting", category: "Government", note: "Varies by state" },
  { id: 13, name: "Microsoft Partner Network", platform: "Microsoft", type: "Reseller/Tech Contract", value: "Revenue share", eligibility: "IT/Software companies", url: "https://partner.microsoft.com", category: "Tech", note: "Co-sell with Microsoft" },
  { id: 14, name: "Salesforce AppExchange", platform: "Salesforce", type: "ISV/Partner Contract", value: "Revenue share", eligibility: "Salesforce-integrated ISVs", url: "https://appexchange.salesforce.com", category: "Tech", note: "25% rev share" },
  { id: 15, name: "Google Cloud Partner", platform: "Google", type: "Reseller Contract", value: "Commission + credits", eligibility: "Cloud solutions providers", url: "https://cloud.google.com/partners", category: "Tech", note: "Managed service agreements" },
];

// ── FREEBIES / DISCOUNTS (kept from before) ─────────────────────────────────
const FREEBIES = [
  { id: 1, name: "AWS Startup Credits", provider: "Amazon Web Services", value: "$5,000", expiry: "Ongoing", category: "Software" },
  { id: 2, name: "HubSpot CRM Free Tier", provider: "HubSpot", value: "$1,200/yr", expiry: "Ongoing", category: "Software" },
  { id: 3, name: "Google Workspace Trial", provider: "Google", value: "$720", expiry: "Rolling 14-day", category: "Software" },
  { id: 4, name: "Free Legal Consultation", provider: "LegalZoom", value: "$500", expiry: "Ongoing", category: "Services" },
  { id: 5, name: "Coursera Business Plan", provider: "Coursera", value: "$399/yr", expiry: "Ongoing", category: "Education" },
  { id: 6, name: "Notion Team Plan Trial", provider: "Notion", value: "$960/yr", expiry: "Ongoing", category: "Tools" },
  { id: 7, name: "Stripe Atlas Credits", provider: "Stripe", value: "$500", expiry: "Ongoing", category: "Services" },
  { id: 8, name: "Figma Starter Plan", provider: "Figma", value: "$144/yr", expiry: "Ongoing", category: "Tools" },
  { id: 9, name: "LinkedIn Learning Access", provider: "LinkedIn", value: "$360/yr", expiry: "Dec 31, 2026", category: "Education" },
  { id: 10, name: "Cloudflare Pro Trial", provider: "Cloudflare", value: "$240/yr", expiry: "Ongoing", category: "Software" },
  { id: 11, name: "SCORE Mentorship Program", provider: "SCORE", value: "Priceless", expiry: "Ongoing", category: "Services" },
  { id: 12, name: "Canva Pro Trial", provider: "Canva", value: "$120/yr", expiry: "Ongoing", category: "Tools" },
];

const DISCOUNTS = [
  { id: 1, merchant: "Dell Technologies", discount: 25, code: "DREAM25", autoApply: false, expiry: "Rolling", savings: "$375", category: "Tech" },
  { id: 2, merchant: "WeWork", discount: 30, code: null, autoApply: true, expiry: "Rolling", savings: "$540/mo", category: "Office" },
  { id: 3, merchant: "Mailchimp", discount: 50, code: "STARTUP50", autoApply: false, expiry: "Rolling", savings: "$150/mo", category: "Marketing" },
  { id: 4, merchant: "United Airlines Business", discount: 15, code: "BIZFLY15", autoApply: false, expiry: "Jun 30, 2026", savings: "$200+", category: "Travel" },
  { id: 5, merchant: "Microsoft 365 Business", discount: 20, code: null, autoApply: true, expiry: "Ongoing", savings: "$48/yr", category: "Tech" },
  { id: 6, merchant: "Staples Business", discount: 10, code: "BIZ10", autoApply: false, expiry: "Ongoing", savings: "$25+", category: "Office" },
  { id: 7, merchant: "SEMrush", discount: 40, code: "GROW40", autoApply: false, expiry: "Rolling", savings: "$480/yr", category: "Marketing" },
  { id: 8, merchant: "Hilton Business Travel", discount: 20, code: null, autoApply: true, expiry: "Dec 31, 2026", savings: "$150+", category: "Travel" },
  { id: 9, merchant: "Lenovo ThinkPad", discount: 35, code: "THINK35", autoApply: false, expiry: "Rolling", savings: "$525", category: "Tech" },
  { id: 10, merchant: "Regus Offices", discount: 25, code: null, autoApply: true, expiry: "Rolling", savings: "$300/mo", category: "Office" },
  { id: 11, merchant: "Adobe Creative Cloud", discount: 60, code: "CREATE60", autoApply: false, expiry: "Rolling", savings: "$420/yr", category: "Marketing" },
  { id: 12, merchant: "Southwest Business", discount: 10, code: "SWBIZ10", autoApply: false, expiry: "Ongoing", savings: "$80+", category: "Travel" },
];

const CATEGORY_ICONS: Record<string, typeof Gift> = {
  Software: Zap, Services: ShieldCheck, Education: GraduationCap,
  Tools: Hammer, Tech: Sparkles, Office: Building2, Marketing: Target, Travel: Truck,
  Government: Landmark, Women: Star, Minority: Users, Agriculture: Truck,
  Fintech: DollarSign, Research: Search, Energy: Zap, Reentry: Users,
  "Small Biz": ShieldCheck, Veterans: ShieldCheck,
  Freelance: Users, "Tech Talent": Sparkles, Consulting: Trophy,
  Finance: Banknote, Infrastructure: Building2,
};

const APPROVAL_COLORS: Record<string, string> = {
  high: "text-green-600 dark:text-green-400",
  medium: "text-yellow-600 dark:text-yellow-400",
  low: "text-red-500 dark:text-red-400",
};

export default function LoansPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const [search, setSearch] = useState("");
  const [tab, setTab] = useState("lenders");

  const filterStr = search.toLowerCase();

  const filteredLoans = LOAN_OFFERS.filter(l =>
    l.lender.toLowerCase().includes(filterStr) || l.type.toLowerCase().includes(filterStr)
  );
  const filteredCards = CREDIT_CARDS.filter(c =>
    c.name.toLowerCase().includes(filterStr) || c.issuer.toLowerCase().includes(filterStr) || c.category.toLowerCase().includes(filterStr)
  );
  const filteredInvestors = INVESTORS.filter(i =>
    i.name.toLowerCase().includes(filterStr) || i.type.toLowerCase().includes(filterStr) || i.focus.toLowerCase().includes(filterStr)
  );
  const filteredGrants = GRANTS.filter(g =>
    g.name.toLowerCase().includes(filterStr) || g.agency.toLowerCase().includes(filterStr) || g.category.toLowerCase().includes(filterStr)
  );
  const filteredContracts = CONTRACTS.filter(c =>
    c.name.toLowerCase().includes(filterStr) || c.type.toLowerCase().includes(filterStr) || c.category.toLowerCase().includes(filterStr)
  );

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Loans, Funding & Contracts — DreamLoans" description="Every loan company, credit card, investor, grant, and contract your bots need." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-loans-title">Loans, Funding & Contracts</h1>
              <p className="text-sm text-muted-foreground mt-1">Every capital source, credit card, investor, grant, and contract available to your bots</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="secondary" className="rounded-full"><Banknote className="h-3 w-3 mr-1.5 text-primary" />{LOAN_OFFERS.length} Lenders</Badge>
              <Badge variant="secondary" className="rounded-full"><CreditCard className="h-3 w-3 mr-1.5 text-blue-500" />{CREDIT_CARDS.length} Cards</Badge>
              <Badge variant="secondary" className="rounded-full"><TrendingUp className="h-3 w-3 mr-1.5 text-violet-500" />{INVESTORS.length} Investors</Badge>
              <Badge variant="secondary" className="rounded-full"><Gift className="h-3 w-3 mr-1.5 text-green-500" />{GRANTS.length} Grants</Badge>
              <Badge variant="secondary" className="rounded-full"><Trophy className="h-3 w-3 mr-1.5 text-yellow-500" />{CONTRACTS.length} Contracts</Badge>
            </div>
          </div>

          <div className="mt-4 relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              placeholder="Search lenders, card names, investors, grants…"
              className="pl-9 rounded-xl"
              value={search}
              onChange={e => setSearch(e.target.value)}
              data-testid="input-funding-search"
            />
          </div>
        </div>

        <div className="p-5 md:p-8 buddy-stagger">
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-8">
            {[
              { label: "Lenders", count: LOAN_OFFERS.length, icon: Banknote, color: "text-primary" },
              { label: "Credit Cards", count: CREDIT_CARDS.length, icon: CreditCard, color: "text-blue-500" },
              { label: "Investors", count: INVESTORS.length, icon: TrendingUp, color: "text-violet-500" },
              { label: "Grants", count: GRANTS.length, icon: Gift, color: "text-green-500" },
              { label: "Contracts", count: CONTRACTS.length, icon: Trophy, color: "text-yellow-500" },
            ].map(s => {
              const Icon = s.icon;
              return (
                <Card key={s.label} className="cursor-pointer hover-elevate" onClick={() => setTab(s.label.toLowerCase().replace(" ", "-"))}>
                  <CardContent className="p-4 text-center">
                    <Icon className={`h-6 w-6 mx-auto mb-2 ${s.color}`} />
                    <p className="text-2xl font-bold">{s.count}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{s.label}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <Tabs value={tab} onValueChange={setTab} data-testid="tabs-loans">
            <TabsList className="flex-wrap h-auto gap-1">
              <TabsTrigger value="lenders" data-testid="tab-lenders"><Banknote className="h-4 w-4 mr-1.5" />Lenders ({filteredLoans.length})</TabsTrigger>
              <TabsTrigger value="credit-cards" data-testid="tab-credit-cards"><CreditCard className="h-4 w-4 mr-1.5" />Credit Cards ({filteredCards.length})</TabsTrigger>
              <TabsTrigger value="investors" data-testid="tab-investors"><TrendingUp className="h-4 w-4 mr-1.5" />Investors ({filteredInvestors.length})</TabsTrigger>
              <TabsTrigger value="grants" data-testid="tab-grants"><Gift className="h-4 w-4 mr-1.5" />Grants ({filteredGrants.length})</TabsTrigger>
              <TabsTrigger value="contracts" data-testid="tab-contracts"><Trophy className="h-4 w-4 mr-1.5" />Contracts ({filteredContracts.length})</TabsTrigger>
              <TabsTrigger value="freebies" data-testid="tab-freebies"><Sparkles className="h-4 w-4 mr-1.5" />Freebies</TabsTrigger>
              <TabsTrigger value="discounts" data-testid="tab-discounts"><Tag className="h-4 w-4 mr-1.5" />Discounts</TabsTrigger>
            </TabsList>

            {/* ── LENDERS ── */}
            <TabsContent value="lenders" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {filteredLoans.map((loan) => {
                  const Icon = loan.icon;
                  return (
                    <Card key={loan.id} data-testid={`card-loan-${loan.id}`} className="hover-elevate">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <Icon className="h-5 w-5 text-primary" />
                          </div>
                          <Badge variant="outline" className="rounded-full text-[10px]">{loan.type}</Badge>
                        </div>
                        <CardTitle className="text-sm mt-2">{loan.lender}</CardTitle>
                        <p className="text-[11px] text-muted-foreground">{loan.note}</p>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex items-baseline gap-1">
                          <span className="text-2xl font-bold">{loan.apr > 0 ? `${loan.apr}%` : "0%"}</span>
                          <span className="text-xs text-muted-foreground">APR</span>
                        </div>
                        <div className="space-y-1.5 text-xs">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-muted-foreground">Amount</span>
                            <span className="font-medium">${loan.minAmount.toLocaleString()} – ${loan.maxAmount.toLocaleString()}</span>
                          </div>
                          {loan.termMonths > 0 && (
                            <div className="flex items-center justify-between gap-2">
                              <span className="text-muted-foreground">Max Term</span>
                              <span className="font-medium">{loan.termMonths} months</span>
                            </div>
                          )}
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-muted-foreground">Approval</span>
                            <span className={`font-medium capitalize ${APPROVAL_COLORS[loan.approval]}`}>
                              {loan.approval === "high" && <CheckCircle2 className="h-3 w-3 inline mr-0.5" />}
                              {loan.approval}
                            </span>
                          </div>
                        </div>
                        <a href={loan.url} target="_blank" rel="noopener noreferrer" className="block">
                          <Button className="w-full" size="sm" data-testid={`button-apply-loan-${loan.id}`}>
                            <ExternalLink className="h-3.5 w-3.5 mr-1.5" />Apply Now
                          </Button>
                        </a>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            {/* ── CREDIT CARDS ── */}
            <TabsContent value="credit-cards" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredCards.map((card) => (
                  <Card key={card.id} data-testid={`card-cc-${card.id}`} className="hover-elevate">
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-3 min-w-0">
                          <div className="h-10 w-10 rounded-xl bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                            <CreditCard className="h-5 w-5 text-blue-500" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm font-semibold leading-tight">{card.name}</p>
                            <p className="text-xs text-muted-foreground">{card.issuer}</p>
                          </div>
                        </div>
                        <Badge variant="outline" className="rounded-full text-[10px] flex-shrink-0">{card.category}</Badge>
                      </div>
                      <div className="bg-primary/5 rounded-xl p-3 space-y-1.5 text-xs">
                        <div className="flex justify-between gap-2">
                          <span className="text-muted-foreground">Reward</span>
                          <span className="font-medium text-right max-w-[60%]">{card.reward}</span>
                        </div>
                        <div className="flex justify-between gap-2">
                          <span className="text-muted-foreground">Annual Fee</span>
                          <span className="font-medium">{card.annualFee === 0 ? "$0" : `$${card.annualFee}`}</span>
                        </div>
                        <div className="flex justify-between gap-2">
                          <span className="text-muted-foreground">Sign-up Bonus</span>
                          <span className="font-medium text-green-600 dark:text-green-400 text-right max-w-[60%]">{card.bonus}</span>
                        </div>
                        <div className="flex justify-between gap-2">
                          <span className="text-muted-foreground">APR</span>
                          <span className="font-medium">{card.apr}</span>
                        </div>
                      </div>
                      <a href={card.url} target="_blank" rel="noopener noreferrer" className="block">
                        <Button className="w-full" size="sm" variant="outline" data-testid={`button-apply-card-${card.id}`}>
                          <ExternalLink className="h-3.5 w-3.5 mr-1.5" />Apply
                        </Button>
                      </a>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* ── INVESTORS ── */}
            <TabsContent value="investors" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredInvestors.map((inv) => (
                  <Card key={inv.id} data-testid={`card-investor-${inv.id}`} className="hover-elevate">
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-3 min-w-0">
                          <div className="h-10 w-10 rounded-xl bg-violet-500/10 flex items-center justify-center flex-shrink-0">
                            <TrendingUp className="h-5 w-5 text-violet-500" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm font-semibold leading-tight">{inv.name}</p>
                            <p className="text-xs text-muted-foreground">{inv.type}</p>
                          </div>
                        </div>
                        <Badge variant="outline" className="rounded-full text-[10px] flex-shrink-0">{inv.stage.split(" ")[0]}</Badge>
                      </div>
                      <div className="space-y-1.5 text-xs bg-primary/5 rounded-xl p-3">
                        <div className="flex justify-between gap-2">
                          <span className="text-muted-foreground">Check Size</span>
                          <span className="font-semibold text-green-600 dark:text-green-400">{inv.check}</span>
                        </div>
                        <div className="flex justify-between gap-2">
                          <span className="text-muted-foreground">Stage</span>
                          <span className="font-medium text-right">{inv.stage}</span>
                        </div>
                        <div className="flex justify-between gap-2">
                          <span className="text-muted-foreground">Focus</span>
                          <span className="font-medium text-right max-w-[55%]">{inv.focus}</span>
                        </div>
                        <div className="flex justify-between gap-2">
                          <span className="text-muted-foreground">Acceptance</span>
                          <span className="font-medium text-red-500 dark:text-red-400">{inv.acceptance}</span>
                        </div>
                      </div>
                      <p className="text-[11px] text-muted-foreground italic">{inv.note}</p>
                      <a href={inv.url} target="_blank" rel="noopener noreferrer" className="block">
                        <Button className="w-full" size="sm" variant="outline" data-testid={`button-apply-investor-${inv.id}`}>
                          <ExternalLink className="h-3.5 w-3.5 mr-1.5" />Apply / Learn More
                        </Button>
                      </a>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* ── GRANTS ── */}
            <TabsContent value="grants" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredGrants.map((grant) => {
                  const CatIcon = CATEGORY_ICONS[grant.category] || Gift;
                  return (
                    <Card key={grant.id} data-testid={`card-grant-${grant.id}`} className="hover-elevate">
                      <CardContent className="p-4 space-y-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-3 min-w-0">
                            <div className="h-10 w-10 rounded-xl bg-green-500/10 flex items-center justify-center flex-shrink-0">
                              <CatIcon className="h-5 w-5 text-green-500" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-sm font-semibold leading-tight">{grant.name}</p>
                              <p className="text-xs text-muted-foreground">{grant.agency}</p>
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-1">
                            <Badge variant="outline" className="rounded-full text-[10px]">{grant.category}</Badge>
                            {!grant.equity && <Badge className="rounded-full text-[10px] bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20">No Equity</Badge>}
                          </div>
                        </div>
                        <div className="space-y-1.5 text-xs bg-primary/5 rounded-xl p-3">
                          <div className="flex justify-between gap-2">
                            <span className="text-muted-foreground">Award</span>
                            <span className="font-semibold text-green-600 dark:text-green-400">{grant.amount}</span>
                          </div>
                          <div className="flex justify-between gap-2">
                            <span className="text-muted-foreground">Deadline</span>
                            <span className="font-medium text-right max-w-[55%]">{grant.deadline}</span>
                          </div>
                          <div className="flex justify-between gap-2">
                            <span className="text-muted-foreground">Who</span>
                            <span className="font-medium text-right max-w-[55%]">{grant.eligibility}</span>
                          </div>
                        </div>
                        <a href={grant.url} target="_blank" rel="noopener noreferrer" className="block">
                          <Button className="w-full" size="sm" data-testid={`button-apply-grant-${grant.id}`}>
                            <Gift className="h-3.5 w-3.5 mr-1.5" />Apply for Grant
                          </Button>
                        </a>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            {/* ── CONTRACTS ── */}
            <TabsContent value="contracts" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredContracts.map((contract) => {
                  const CatIcon = CATEGORY_ICONS[contract.category] || Trophy;
                  return (
                    <Card key={contract.id} data-testid={`card-contract-${contract.id}`} className="hover-elevate">
                      <CardContent className="p-4 space-y-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-3 min-w-0">
                            <div className="h-10 w-10 rounded-xl bg-yellow-500/10 flex items-center justify-center flex-shrink-0">
                              <CatIcon className="h-5 w-5 text-yellow-500" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-sm font-semibold leading-tight">{contract.name}</p>
                              <p className="text-xs text-muted-foreground">{contract.platform}</p>
                            </div>
                          </div>
                          <Badge variant="outline" className="rounded-full text-[10px] flex-shrink-0">{contract.category}</Badge>
                        </div>
                        <div className="space-y-1.5 text-xs bg-primary/5 rounded-xl p-3">
                          <div className="flex justify-between gap-2">
                            <span className="text-muted-foreground">Type</span>
                            <span className="font-medium text-right max-w-[60%]">{contract.type}</span>
                          </div>
                          <div className="flex justify-between gap-2">
                            <span className="text-muted-foreground">Value</span>
                            <span className="font-semibold text-yellow-600 dark:text-yellow-400">{contract.value}</span>
                          </div>
                          <div className="flex justify-between gap-2">
                            <span className="text-muted-foreground">Eligibility</span>
                            <span className="font-medium text-right max-w-[60%]">{contract.eligibility}</span>
                          </div>
                        </div>
                        <p className="text-[11px] text-muted-foreground italic">{contract.note}</p>
                        <a href={contract.url} target="_blank" rel="noopener noreferrer" className="block">
                          <Button className="w-full" size="sm" variant="outline" data-testid={`button-apply-contract-${contract.id}`}>
                            <ExternalLink className="h-3.5 w-3.5 mr-1.5" />View Contract
                          </Button>
                        </a>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            {/* ── FREEBIES ── */}
            <TabsContent value="freebies" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {FREEBIES.map((freebie) => {
                  const CatIcon = CATEGORY_ICONS[freebie.category] || Gift;
                  return (
                    <Card key={freebie.id} data-testid={`card-freebie-${freebie.id}`} className="hover-elevate">
                      <CardContent className="p-4 space-y-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-3 min-w-0">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                              <CatIcon className="h-5 w-5 text-primary" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-sm font-semibold truncate">{freebie.name}</p>
                              <p className="text-xs text-muted-foreground truncate">{freebie.provider}</p>
                            </div>
                          </div>
                          <Badge variant="outline" className="rounded-full text-[10px] flex-shrink-0">{freebie.category}</Badge>
                        </div>
                        <div className="flex items-center justify-between gap-2">
                          <div>
                            <p className="text-xs text-muted-foreground">Value</p>
                            <p className="text-lg font-bold text-green-600 dark:text-green-400">{freebie.value}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-muted-foreground">Expires</p>
                            <p className="text-xs font-medium flex items-center gap-1"><Clock className="h-3 w-3" />{freebie.expiry}</p>
                          </div>
                        </div>
                        <Button className="w-full" size="sm" variant="outline" data-testid={`button-claim-freebie-${freebie.id}`}>
                          <Gift className="h-4 w-4 mr-1.5" />Claim Free
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            {/* ── DISCOUNTS ── */}
            <TabsContent value="discounts" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {DISCOUNTS.map((deal) => {
                  const CatIcon = CATEGORY_ICONS[deal.category] || Tag;
                  return (
                    <Card key={deal.id} data-testid={`card-discount-${deal.id}`} className="hover-elevate">
                      <CardContent className="p-4 space-y-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-3 min-w-0">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                              <CatIcon className="h-5 w-5 text-primary" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-sm font-semibold truncate">{deal.merchant}</p>
                              <Badge variant="outline" className="rounded-full text-[10px] mt-0.5">{deal.category}</Badge>
                            </div>
                          </div>
                          <div className="text-right flex-shrink-0">
                            <p className="text-2xl font-bold text-green-600 dark:text-green-400">{deal.discount}%</p>
                            <p className="text-[10px] text-muted-foreground">off</p>
                          </div>
                        </div>
                        <div className="flex items-center justify-between gap-2 text-xs">
                          <div><p className="text-muted-foreground">Savings</p><p className="font-semibold">{deal.savings}</p></div>
                          <div className="text-right"><p className="text-muted-foreground">Expires</p><p className="font-medium">{deal.expiry}</p></div>
                        </div>
                        {deal.code ? (
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-muted/50 rounded-md px-3 py-1.5 font-mono text-xs text-center tracking-wider">{deal.code}</div>
                            <Button size="icon" variant="outline" data-testid={`button-copy-code-${deal.id}`}>
                              <Copy className="h-4 w-4" />
                            </Button>
                          </div>
                        ) : (
                          <Badge variant="secondary" className="w-full justify-center rounded-full">
                            <Zap className="h-3 w-3 mr-1.5" />Auto-Applied
                          </Badge>
                        )}
                        <Button className="w-full" size="sm" data-testid={`button-get-discount-${deal.id}`}>
                          <Percent className="h-4 w-4 mr-1.5" />Get Discount
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppShell>
  );
}
