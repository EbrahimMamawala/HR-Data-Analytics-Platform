"use client"

import { useState } from "react"
import { SignIn, SignUp } from "@clerk/nextjs"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Building2 } from "lucide-react"

export default function LoginPage() {
  const [isSignUp, setIsSignUp] = useState(false)

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-primary/10 p-3">
              <Building2 className="h-8 w-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center">
            HR Analytics Platform
          </CardTitle>
          <CardDescription className="text-center">
            {isSignUp ? "Create an account to access your dashboard" : "Enter your credentials to access your dashboard"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isSignUp ? (
            <SignUp
              routing="hash"
              appearance={{ elements: { rootBox: "rounded-lg shadow-lg" } }}
            />
          ) : (
            <SignIn
              routing="hash"
              appearance={{ elements: { rootBox: "rounded-lg shadow-lg" } }}
            />
          )}
        </CardContent>
        <CardFooter className="flex justify-center">
          {isSignUp ? (
            <p className="text-sm text-muted-foreground">
              Already have an account?{" "}
              <Button
                variant="link"
                className="p-0 h-auto text-sm"
                onClick={() => setIsSignUp(false)}
              >
                Sign In
              </Button>
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">
              Don't have an account?{" "}
              <Button
                variant="link"
                className="p-0 h-auto text-sm"
                onClick={() => setIsSignUp(true)}
              >
                Sign Up
              </Button>
            </p>
          )}
        </CardFooter>
      </Card>
    </div>
  )
}
