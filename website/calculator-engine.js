const safe = (value, fallback = 0) => Number.isFinite(Number(value)) ? Number(value) : fallback;
const ratio = (numerator, denominator) => denominator > 0 ? numerator / denominator : 0;

export function calculateBotTemplate(templateId, input) {
  const v = Object.fromEntries(Object.entries(input).map(([key, value]) => [key, safe(value)]));
  switch (templateId) {
    case 'real_estate_flip': {
      const totalCost = v.purchase_price + v.repair_costs + (v.holding_cost_monthly * v.holding_months) + v.selling_costs;
      const net = v.after_repair_value - totalCost;
      return { maximum_offer: (v.after_repair_value * 0.70) - v.repair_costs, total_cost: totalCost, net_value: net, roi: ratio(net, totalCost) * 100 };
    }
    case 'car_flip': {
      const totalCost = v.purchase_price + v.repair_costs + v.transport_costs + v.fees;
      const net = v.sale_price - totalCost;
      return { total_cost: totalCost, net_value: net, roi: ratio(net, totalCost) * 100, margin: ratio(net, v.sale_price) * 100 };
    }
    case 'commerce_margin': {
      const gross = v.units * v.sale_price;
      const returnLoss = gross * (v.return_rate / 100);
      const totalCost = (v.units * v.unit_cost) + v.fees + v.marketing_cost + returnLoss;
      const net = gross - totalCost;
      const contribution = (v.sale_price * (1 - v.return_rate / 100)) - v.unit_cost;
      return { gross_value: gross, total_cost: totalCost, net_value: net, margin: ratio(net, gross) * 100, break_even_units: contribution > 0 ? (v.fees + v.marketing_cost) / contribution : 0 };
    }
    case 'sales_funnel': {
      const converted = v.leads * (v.conversion_rate / 100);
      const gross = converted * v.average_value;
      const net = gross - v.campaign_cost;
      return { converted, gross_value: gross, cost_per_acquisition: ratio(v.campaign_cost, converted), net_value: net, roi: ratio(net, v.campaign_cost) * 100 };
    }
    case 'cash_flow': {
      const inflow = v.monthly_income * v.months;
      const outflow = v.initial_investment + (v.monthly_expense * v.months);
      const net = inflow - outflow;
      return { total_inflow: inflow, total_outflow: outflow, net_value: net, roi: ratio(net, outflow) * 100, runway: ratio(v.opening_cash, v.monthly_expense) };
    }
    case 'software_unit_economics': {
      const revenue = v.users * v.monthly_price;
      const monthlyNet = revenue - (v.users * v.variable_cost) - v.fixed_cost;
      const periodNet = (monthlyNet * v.months) - v.build_cost;
      return { monthly_revenue: revenue, monthly_net: monthlyNet, payback: monthlyNet > 0 ? v.build_cost / monthlyNet : 0, net_value: periodNet, roi: ratio(periodNet, v.build_cost) * 100 };
    }
    case 'risk_reduction': {
      const baseline = v.events * (v.baseline_probability / 100) * v.average_loss;
      const residual = v.events * (v.residual_probability / 100) * v.average_loss;
      const avoided = baseline - residual;
      const net = avoided - v.mitigation_cost;
      return { baseline_risk: baseline, residual_risk: residual, avoided_loss: avoided, net_value: net, roi: ratio(net, v.mitigation_cost) * 100 };
    }
    case 'learning_outcomes': {
      const completers = v.learners * (v.completion_rate / 100);
      const gross = completers * (v.improvement_rate / 100) * v.value_per_learner;
      const net = gross - v.program_cost;
      return { completers, gross_value: gross, cost_per_completion: ratio(v.program_cost, completers), net_value: net, roi: ratio(net, v.program_cost) * 100 };
    }
    case 'project_estimate': {
      const hours = v.units * v.hours_per_unit;
      const labor = hours * v.hourly_cost;
      const subtotal = labor + v.materials;
      const contingency = subtotal * (v.contingency_rate / 100);
      return { labor_hours: hours, labor_cost: labor, subtotal, contingency, total_cost: subtotal + contingency };
    }
    case 'operations_efficiency': {
      const baselineHours = (v.items * v.minutes_per_item) / 60;
      const savedHours = baselineHours * (v.time_reduction / 100);
      const laborValue = savedHours * v.hourly_value;
      const errorCost = v.items * (v.error_rate / 100) * v.cost_per_error;
      return { baseline_hours: baselineHours, hours_saved: savedHours, labor_value: laborValue, error_cost: errorCost, net_value: laborValue + errorCost - v.tool_cost };
    }
    case 'creative_project': {
      const hours = v.units * v.hours_per_unit;
      const totalCost = (hours * v.hourly_cost) + v.asset_cost + v.distribution_cost;
      const net = v.expected_revenue - totalCost;
      return { labor_hours: hours, total_cost: totalCost, break_even: totalCost, net_value: net, roi: ratio(net, totalCost) * 100 };
    }
    case 'subscription': {
      const revenue = v.subscribers * v.monthly_price;
      const monthlyNet = revenue - (v.subscribers * v.variable_cost) - v.fixed_cost;
      const churnRate = v.monthly_churn / 100;
      return { monthly_revenue: revenue, monthly_net: monthlyNet, annual_net: monthlyNet * 12, churned: v.subscribers * churnRate, contribution_ltv: churnRate > 0 ? Math.max(0, v.monthly_price - v.variable_cost) / churnRate : 0 };
    }
    case 'research_value': {
      const timeValue = v.hours_saved * v.hourly_value;
      const gross = timeValue + v.avoided_cost;
      const net = gross - v.tool_cost;
      return { time_value: timeValue, gross_value: gross, net_value: net, value_per_decision: ratio(net, v.decisions), roi: ratio(net, v.tool_cost) * 100 };
    }
    default:
      throw new Error(`Unsupported calculator template: ${templateId}`);
  }
}

export function formatCalculatorValue(value, unit) {
  const safeValue = Number.isFinite(value) ? value : 0;
  if (unit === 'currency') return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(safeValue);
  if (unit === 'percent') return `${safeValue.toFixed(2)}%`;
  if (unit === 'months') return `${safeValue.toFixed(1)} months`;
  if (unit === 'hours') return `${safeValue.toFixed(1)} hours`;
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(safeValue);
}
