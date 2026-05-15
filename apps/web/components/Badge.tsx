import clsx from "clsx";

type BadgeProps = {
  tone: "low" | "medium" | "high" | "neutral";
  children: React.ReactNode;
};

export function Badge({ tone, children }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex h-7 items-center rounded px-2 text-xs font-semibold uppercase tracking-normal",
        tone === "low" && "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200",
        tone === "medium" && "bg-amber-50 text-warning ring-1 ring-amber-200",
        tone === "high" && "bg-red-50 text-danger ring-1 ring-red-200",
        tone === "neutral" && "bg-slate-100 text-slate-700 ring-1 ring-slate-200"
      )}
    >
      {children}
    </span>
  );
}
