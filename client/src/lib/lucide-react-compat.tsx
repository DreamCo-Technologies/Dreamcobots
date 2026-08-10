import * as React from "react"

/**
 * Generic code-hosting/network icon used where older DreamCo UI imported the
 * removed Lucide `Github` brand export. This intentionally is not a brand logo.
 */
export const Github = React.forwardRef<SVGSVGElement, React.SVGProps<SVGSVGElement>>(
  ({ className, width = 24, height = 24, strokeWidth = 2, ...props }, ref) => (
    <svg
      ref={ref}
      className={className}
      width={width}
      height={height}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      <circle cx="6" cy="6" r="2" />
      <circle cx="18" cy="6" r="2" />
      <circle cx="12" cy="18" r="2" />
      <path d="M8 6h8" />
      <path d="M7.5 7.5 11 16" />
      <path d="m16.5 7.5-3.5 8.5" />
    </svg>
  )
)
Github.displayName = "Github"
