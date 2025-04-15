import { Roles } from '@/types/globals'
import { currentUser } from '@clerk/nextjs/server'

export const checkRole = async (role: Roles) => {
  const user = await currentUser()
  console.log("User role: " , user?.publicMetadata.role)
  console.log("Checking role: " , role)
  return user?.publicMetadata.role === role
}
