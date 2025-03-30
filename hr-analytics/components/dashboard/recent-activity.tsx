import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

const activities = [
  {
    id: 1,
    user: {
      name: "Sarah Johnson",
      department: "Engineering",
      image: "/placeholder.svg?height=32&width=32",
    },
    action: "joined",
    date: "2 hours ago",
  },
  {
    id: 2,
    user: {
      name: "Michael Chen",
      department: "Marketing",
      image: "/placeholder.svg?height=32&width=32",
    },
    action: "promoted to Senior Marketing Specialist",
    date: "Yesterday",
  },
  {
    id: 3,
    user: {
      name: "Emily Rodriguez",
      department: "HR",
      image: "/placeholder.svg?height=32&width=32",
    },
    action: "updated their profile",
    date: "2 days ago",
  },
  {
    id: 4,
    user: {
      name: "David Kim",
      department: "Finance",
      image: "/placeholder.svg?height=32&width=32",
    },
    action: "left the company",
    date: "3 days ago",
  },
  {
    id: 5,
    user: {
      name: "Jessica Patel",
      department: "Product",
      image: "/placeholder.svg?height=32&width=32",
    },
    action: "transferred to Design team",
    date: "1 week ago",
  },
]

export function RecentActivity() {
  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div key={activity.id} className="flex items-start gap-4">
          <Avatar className="h-9 w-9">
            <AvatarImage src={activity.user.image} alt={activity.user.name} />
            <AvatarFallback>{activity.user.name.charAt(0)}</AvatarFallback>
          </Avatar>
          <div className="space-y-1">
            <p className="text-sm font-medium leading-none">
              {activity.user.name}
              <span className="text-muted-foreground font-normal"> {activity.action}</span>
            </p>
            <p className="text-xs text-muted-foreground">
              {activity.user.department} • {activity.date}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}

