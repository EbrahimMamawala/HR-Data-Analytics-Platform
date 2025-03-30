"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, Users, TrendingUp, Home } from "lucide-react"
import { cn } from "@/lib/utils"

const sidebarLinks = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "Employee Data",
    href: "/dashboard/employees",
    icon: Users,
  },
  {
    title: "Diversity Analysis",
    href: "/dashboard/diversity",
    icon: BarChart3,
  },
  {
    title: "Attrition Prediction",
    href: "/dashboard/attrition",
    icon: TrendingUp,
  },
]

export function DashboardSidebar() {
  const pathname = usePathname()

  return (
    <div className="hidden border-r bg-gray-50/40 lg:block">
      <div className="flex h-full max-h-screen flex-col gap-2">
        <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
          <Link href="/dashboard" className="flex items-center gap-2 font-semibold">
            <BarChart3 className="h-6 w-6" />
            <span className="text-lg">HR Analytics</span>
          </Link>
        </div>
        <div className="flex-1">
          <nav className="grid items-start px-2 text-sm font-medium">
            {sidebarLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-primary",
                  pathname === link.href ? "bg-primary/10 text-primary" : "text-muted-foreground",
                )}
              >
                <link.icon className="h-4 w-4" />
                {link.title}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </div>
  )
}

