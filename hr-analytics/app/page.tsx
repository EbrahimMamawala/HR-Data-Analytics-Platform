import { redirect } from "next/navigation"
import { auth } from "@clerk/nextjs/server"
import { headers } from "next/headers"
import LoginPage from "@/components/login-page"
import { SignedIn, SignedOut } from "@clerk/nextjs"

export default async function Home() {
  const { userId } = await auth()

  if (userId) {
    redirect("/dashboard")
  }

  return (
    <>
      <SignedIn>
        {/* Empty since it redirects automatically */}
      </SignedIn>
      <SignedOut>
          <LoginPage />
      </SignedOut>
    </>
  )
}
