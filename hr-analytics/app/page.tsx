import { redirect } from "next/navigation"
import { auth } from "@clerk/nextjs/server"
import { headers } from "next/headers"
import LoginPage from "@/components/login-page"

export default async function Home() {
  const { userId } = await auth()

  if (userId) {
    redirect("/dashboard")
  }

  return <LoginPage />
}
