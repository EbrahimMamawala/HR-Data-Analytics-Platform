'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { 
  Card, CardContent, CardHeader, CardTitle 
} from '@/components/ui/card'
import { 
  Form, FormField, FormItem, FormLabel, FormControl 
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { 
  Select, SelectTrigger, SelectValue, 
  SelectContent, SelectItem 
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, AlertCircle } from 'lucide-react'

const formSchema = z.object({
  firstName: z.string().min(1, 'First name is required'),
  lastName:  z.string().min(1, 'Last name is required'),
  email:     z.string().email('Invalid email address'),
  department:z.string(),
  position:  z.string(),
  status:    z.string(),
  joinDate:  z.string().min(1, 'Join date is required'),
  gender:    z.string(),
  age:       z.string().min(1, 'Age is required'),
})

export default function AddEmployeeForm() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: string; text: string } | null>(null)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      department: 'IT',
      position: 'Analyst',
      status: 'Active',
      joinDate: '',
      gender: 'Male',
      age: '',
    },
  })

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    setLoading(true)
    setMessage(null)
    try {
      const res = await fetch('/api/employees', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      })
      const data = await res.json()
      if (res.ok) {
        setMessage({ type: 'success', text: 'Employee added successfully!' })
        form.reset()
      } else {
        setMessage({ type: 'error', text: data.error || 'Something went wrong.' })
      }
    } catch {
      setMessage({ type: 'error', text: 'Failed to connect to the server.' })
    } finally {
      setLoading(false)
    }
  }

  const departments = ['IT','HR','Finance','Sales','Marketing','Operations']
  const positions   = ['Analyst','Consultant','Director','Junior Developer','Manager','Senior Developer']
  const statuses    = ['Active','Terminated']
  const genders     = ['Male','Female','Other']

  return (
    <div className="container mx-auto py-8 px-4 max-w-3xl">
      <Card className="border-0 shadow-lg">
        <CardHeader className="bg-slate-50 rounded-t-lg">
          <CardTitle className="text-2xl font-medium text-slate-800">
            Add New Employee
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          {message && (
            <Alert
              className={`mb-6 ${
                message.type === 'success'
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-rose-50 text-rose-800 border-rose-200'
              }`}
            >
              <div className="flex items-center gap-2">
                {message.type === 'success' ? (
                  <CheckCircle className="h-5 w-5 text-emerald-500" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-rose-500" />
                )}
                <AlertDescription>{message.text}</AlertDescription>
              </div>
            </Alert>
          )}

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* First & Last Name */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {['firstName','lastName'].map((field, idx) => (
                  <FormField
                    key={field}
                    control={form.control}
                    name={field as 'firstName' | 'lastName'}
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{field.name === 'firstName' ? 'First Name' : 'Last Name'}</FormLabel>
                        <FormControl>
                          <Input placeholder={field.name === 'firstName' ? 'John' : 'Doe'} {...field} />
                        </FormControl>
                      </FormItem>
                    )}
                  />
                ))}
              </div>

              {/* Email */}
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input type="email" placeholder="john.doe@example.com" {...field} />
                    </FormControl>
                  </FormItem>
                )}
              />

              {/* Dept & Position */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="department"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Department</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                          {departments.map((d) => (
                            <SelectItem key={d} value={d}>{d}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="position"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Position</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                          {positions.map((p) => (
                            <SelectItem key={p} value={p}>{p}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </FormItem>
                  )}
                />
              </div>

              {/* Status & Gender */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="status"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Status</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                          {statuses.map((s) => (
                            <SelectItem key={s} value={s}>{s}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="gender"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Gender</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                          {genders.map((g) => (
                            <SelectItem key={g} value={g}>{g}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </FormItem>
                  )}
                />
              </div>

              {/* Join Date & Age */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="joinDate"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Join Date</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="age"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Age</FormLabel>
                      <FormControl>
                        <Input type="number" min={0} {...field} />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                disabled={loading}
              >
                {loading ? 'Saving…' : 'Add Employee'}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}
