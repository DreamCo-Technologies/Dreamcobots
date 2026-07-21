#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const INCOMPLETE_STATUSES = new Set(['todo', 'to do', 'pending', 'not started', 'incomplete', 'in_progress']);
const ALLOWED_BOT_STATUSES = new Set(['active', 'idle', 'paused', 'degraded', 'maintenance']);

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function validateBotsConfig(botsConfig) {
  const issues = [];
  const bots = Array.isArray(botsConfig) ? botsConfig : [];

  if (bots.length === 0) {
    issues.push('bots.json must define at least one bot');
  }

  bots.forEach((bot, index) => {
    if (!isPlainObject(bot)) {
      issues.push(`bots.json bot[${index}] must be an object`);
      return;
    }

    if (!String(bot.name || '').trim()) {
      issues.push(`bots.json bot[${index}] is missing name`);
    }

    const status = String(bot.status || '').trim().toLowerCase();
    if (!status) {
      issues.push(`bots.json bot[${index}] is missing status`);
    } else if (!ALLOWED_BOT_STATUSES.has(status)) {
      issues.push(`bots.json bot[${index}] has unsupported status "${bot.status}"`);
    }
  });

  return issues;
}

function validateCommandCenterConfig(commandCenterConfig) {
  const issues = [];
  const lanes = Array.isArray(commandCenterConfig?.parallel_lanes)
    ? commandCenterConfig.parallel_lanes
    : [];

  if (lanes.length === 0) {
    issues.push('command_center.json must define at least one parallel lane');
  }

  lanes.forEach((lane, index) => {
    if (!isPlainObject(lane)) {
      issues.push(`command_center.json lane[${index}] must be an object`);
      return;
    }

    if (!String(lane.lane_id || '').trim()) {
      issues.push(`command_center.json lane[${index}] is missing lane_id`);
    }

    if (!String(lane.owner || '').trim()) {
      issues.push(`command_center.json lane[${index}] is missing owner`);
    }

    const normalizedStatus = String(lane.status || '').trim().toLowerCase();
    if (!normalizedStatus) {
      issues.push(`command_center.json lane[${index}] is missing status`);
    } else if (INCOMPLETE_STATUSES.has(normalizedStatus)) {
      issues.push(
        `command_center.json lane[${index}] (${lane.lane_id || 'unknown'}) has incomplete status "${lane.status}"`
      );
    }

    const shipDecision = String(lane.ship_decision || '').trim().toLowerCase();
    if (!shipDecision) {
      issues.push(`command_center.json lane[${index}] is missing ship_decision`);
    } else if (shipDecision !== 'ship') {
      issues.push(
        `command_center.json lane[${index}] (${lane.lane_id || 'unknown'}) has non-final ship_decision "${lane.ship_decision}"`
      );
    }
  });

  return issues;
}

function runAudit(baseDir = process.cwd()) {
  const botsPath = path.join(baseDir, 'dreamco-control-tower', 'config', 'bots.json');
  const commandCenterPath = path.join(baseDir, 'dreamco-control-tower', 'config', 'command_center.json');

  const botsConfig = JSON.parse(fs.readFileSync(botsPath, 'utf8'));
  const commandCenterConfig = JSON.parse(fs.readFileSync(commandCenterPath, 'utf8'));

  const issues = [
    ...validateBotsConfig(botsConfig),
    ...validateCommandCenterConfig(commandCenterConfig)
  ];

  return {
    ok: issues.length === 0,
    checked: {
      botsPath,
      commandCenterPath,
      totalBots: Array.isArray(botsConfig) ? botsConfig.length : 0,
      totalLanes: Array.isArray(commandCenterConfig.parallel_lanes)
        ? commandCenterConfig.parallel_lanes.length
        : 0
    },
    issues
  };
}

if (require.main === module) {
  try {
    const result = runAudit();
    if (!result.ok) {
      console.error('Agent audit failed:');
      result.issues.forEach((issue) => console.error(`- ${issue}`));
      process.exitCode = 1;
    } else {
      console.log(
        `Agent audit passed (${result.checked.totalBots} bots, ${result.checked.totalLanes} lanes checked).`
      );
    }
  } catch (error) {
    console.error(`Agent audit crashed: ${error.message}`);
    process.exitCode = 1;
  }
}

module.exports = {
  validateBotsConfig,
  validateCommandCenterConfig,
  runAudit
};
