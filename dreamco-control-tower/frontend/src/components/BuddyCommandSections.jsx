import {
  CORE_OPERATIONAL_GROUPS,
  MUST_HAVE_BUTTONS,
  PINNED_TOP_ACTIONS,
  SIDEBAR_STRUCTURE,
} from './buddyCommandCatalog.js';

function ActionButton({ label, onRun }) {
  return (
    <button
      type="button"
      onClick={() => onRun(label)}
      className="rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-left text-xs text-slate-200 transition-colors hover:border-dreamco-accent hover:text-white"
    >
      {label}
    </button>
  );
}

function ActionGroup({ title, icon, buttons, onRun }) {
  return (
    <section className="rounded-xl border border-slate-700 bg-dreamco-card p-4">
      <h3 className="mb-3 text-sm font-semibold text-slate-100">
        {icon} {title}
      </h3>
      <div className="grid grid-cols-1 gap-2 md:grid-cols-2 xl:grid-cols-3">
        {buttons.map((label) => (
          <ActionButton key={label} label={label} onRun={onRun} />
        ))}
      </div>
    </section>
  );
}

export default function BuddyCommandSections({ onRunCommand = () => {} }) {
  return (
    <div className="mt-6 space-y-4">
      <section className="rounded-xl border border-dreamco-accent/60 bg-dreamco-card p-4">
        <h3 className="text-sm font-semibold text-white">📌 Pinned Top Navigation Actions</h3>
        <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {PINNED_TOP_ACTIONS.map((label) => (
            <ActionButton key={label} label={label} onRun={onRunCommand} />
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-slate-700 bg-dreamco-card p-4">
        <h3 className="text-sm font-semibold text-slate-100">🧭 Command Center Sidebar Draft</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {SIDEBAR_STRUCTURE.map((item) => (
            <span
              key={item}
              className="rounded-full border border-slate-600 px-3 py-1 text-xs text-slate-300"
            >
              {item}
            </span>
          ))}
        </div>
      </section>

      {CORE_OPERATIONAL_GROUPS.map((group) => (
        <ActionGroup
          key={group.title}
          title={group.title}
          icon={group.icon}
          buttons={group.buttons}
          onRun={onRunCommand}
        />
      ))}

      <ActionGroup
        title="Additional Must-Have Command Center Buttons"
        icon="✨"
        buttons={MUST_HAVE_BUTTONS}
        onRun={onRunCommand}
      />
    </div>
  );
}
