import { ReactNode } from "react";
import { cn } from "@/lib/utils";

export default function EmptyState(props: {
  icon: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
  "data-testid"?: string;
}) {
  return (
    <div
      className={cn(
        "buddy-card buddy-noise rounded-3xl p-8 md:p-10 border-border/60",
        "flex flex-col items-center text-center",
        props.className
      )}
      data-testid={props["data-testid"]}
    >
      <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-primary/18 via-accent/10 to-transparent border border-border/60 shadow-sm flex items-center justify-center text-primary">
        {props.icon}
      </div>
      <h3 className="mt-4 text-xl md:text-2xl">{props.title}</h3>
      {props.description ? (
        <p className="mt-2 text-sm md:text-base text-muted-foreground max-w-[56ch]">
          {props.description}
        </p>
      ) : null}
      {props.action ? <div className="mt-6">{props.action}</div> : null}
    </div>
  );
}
