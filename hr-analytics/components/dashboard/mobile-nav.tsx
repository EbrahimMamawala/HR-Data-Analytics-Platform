"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, Users, TrendingUp, Home, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
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

export function MobileNav() {
  const pathname = usePathname()
  const [open, setOpen] = React.useState(false)

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" size="icon" className="lg:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle Menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-[240px] sm:w-[300px]">
        <div className="flex h-full flex-col">
          <div className="flex items-center gap-2 border-b py-4">
            <BarChart3 className="h-6 w-6" />
            <span className="text-lg font-semibold">HR Analytics</span>
          </div>
          <nav className="grid gap-2 py-4">
            {sidebarLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
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
      </SheetContent>
    </Sheet>
  )
}

