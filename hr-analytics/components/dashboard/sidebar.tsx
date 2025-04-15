'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { BarChart3, Users, TrendingUp, Home, CirclePlus } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUser } from '@clerk/nextjs'

const sidebarLinks = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: Home,
  },
  {
    title: 'Employee Data',
    href: '/dashboard/employees',
    icon: Users,
  },
  {
    title: 'Diversity Analysis',
    href: '/dashboard/diversity',
    icon: BarChart3,
  },
  {
    title: 'Attrition Prediction',
    href: '/dashboard/attrition',
    icon: TrendingUp,
  },
  {
    title: 'Add Employee Data',
    href: '/dashboard/addEmployeeData',
    icon: CirclePlus,
  },
]

export function DashboardSidebar() {
  const pathname = usePathname()
  const { isLoaded, user } = useUser()

  // while Clerk is loading your user, don’t show HR‑only links
  const role = isLoaded ? user?.publicMetadata?.role : undefined

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
            {sidebarLinks.map((link) => {
              // hide the Add Employee Data link if the user is not HR
              if (
                link.href === '/dashboard/addEmployeeData' &&
                role !== 'hr'
              ) {
                return null
              }

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-primary',
                    pathname === link.href
                      ? 'bg-primary/10 text-primary'
                      : 'text-muted-foreground'
                  )}
                >
                  <link.icon className="h-4 w-4" />
                  {link.title}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </div>
  )
}
