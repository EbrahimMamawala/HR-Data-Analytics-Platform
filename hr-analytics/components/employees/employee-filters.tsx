"use client"

import * as React from "react"
import { Check, ChevronsUpDown, Filter } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { cn } from "@/lib/utils"
import { Card, CardContent } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Slider } from "@/components/ui/slider"

const departments = [
  { label: "All Departments", value: "all" },
  { label: "Engineering", value: "engineering" },
  { label: "Marketing", value: "marketing" },
  { label: "Finance", value: "finance" },
  { label: "HR", value: "hr" },
  { label: "Product", value: "product" },
  { label: "Design", value: "design" },
  { label: "Sales", value: "sales" },
  { label: "Customer Support", value: "support" },
]

export function EmployeeFilters() {
  const [open, setOpen] = React.useState(false)
  const [department, setDepartment] = React.useState(departments[0])
  const [gender, setGender] = React.useState("all")
  const [ageRange, setAgeRange] = React.useState([20, 60])
  const [showFilters, setShowFilters] = React.useState(false)

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button variant="outline" role="combobox" aria-expanded={open} className="w-[200px] justify-between">
              {department.label}
              <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-[200px] p-0">
            <Command>
              <CommandInput placeholder="Search department..." />
              <CommandList>
                <CommandEmpty>No department found.</CommandEmpty>
                <CommandGroup>
                  {departments.map((dept) => (
                    <CommandItem
                      key={dept.value}
                      value={dept.value}
                      onSelect={() => {
                        setDepartment(dept)
                        setOpen(false)
                      }}
                    >
                      <Check
                        className={cn("mr-2 h-4 w-4", department.value === dept.value ? "opacity-100" : "opacity-0")}
                      />
                      {dept.label}
                    </CommandItem>
                  ))}
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>

        <Button variant="outline" onClick={() => setShowFilters(!showFilters)} className="gap-2">
          <Filter className="h-4 w-4" />
          Filters
        </Button>
      </div>

      {showFilters && (
        <Card>
          <CardContent className="pt-6">
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              <div className="space-y-2">
                <Label>Gender</Label>
                <RadioGroup
                  defaultValue="all"
                  value={gender}
                  onValueChange={setGender}
                  className="flex flex-col space-y-1"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="all" id="all" />
                    <Label htmlFor="all">All</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="male" id="male" />
                    <Label htmlFor="male">Male</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="female" id="female" />
                    <Label htmlFor="female">Female</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="other" id="other" />
                    <Label htmlFor="other">Other</Label>
                  </div>
                </RadioGroup>
              </div>

              <div className="space-y-2">
                <Label>
                  Age Range: {ageRange[0]} - {ageRange[1]}
                </Label>
                <Slider
                  defaultValue={[20, 60]}
                  value={ageRange}
                  onValueChange={setAgeRange}
                  min={18}
                  max={70}
                  step={1}
                  className="py-4"
                />
              </div>

              <div className="space-y-2">
                <Label>Status</Label>
                <RadioGroup defaultValue="all" className="flex flex-col space-y-1">
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="all" id="status-all" />
                    <Label htmlFor="status-all">All</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="active" id="status-active" />
                    <Label htmlFor="status-active">Active</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="inactive" id="status-inactive" />
                    <Label htmlFor="status-inactive">Inactive</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="on-leave" id="status-on-leave" />
                    <Label htmlFor="status-on-leave">On Leave</Label>
                  </div>
                </RadioGroup>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

