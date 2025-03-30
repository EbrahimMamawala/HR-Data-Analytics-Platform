"use client"

import { useUser } from "@clerk/nextjs"
import { Card, CardContent } from "@/components/ui/card"

export function WelcomeBanner() {
  const { user, isLoaded } = useUser()

  if (!isLoaded) {
    return (
      <Card className="bg-primary/5 border-primary/20">
        <CardContent className="p-6">
          <div className="h-8 w-48 bg-primary/10 rounded animate-pulse"></div>
          <div className="h-4 w-64 bg-primary/10 rounded mt-2 animate-pulse"></div>
        </CardContent>
      </Card>
    )
  }

  const firstName = user?.firstName || "there"
  const currentTime = new Date()
  const hour = currentTime.getHours()

  let greeting = "Good morning"
  if (hour >= 12 && hour < 17) {
    greeting = "Good afternoon"
  } else if (hour >= 17) {
    greeting = "Good evening"
  }

  return (
    <Card className="bg-primary/5 border-primary/20">
      <CardContent className="p-6">
        <h1 className="text-2xl font-bold text-primary">
          {greeting}, {firstName}!
        </h1>
        <p className="text-muted-foreground mt-1">
          Welcome to your HR Analytics dashboard. Here's what's happening today.
        </p>
      </CardContent>
    </Card>
  )
}

