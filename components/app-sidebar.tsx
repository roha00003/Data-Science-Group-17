"use client"

import * as React from "react"
import { Home, History, Calendar, DollarSign, AlertTriangle, Trash2 } from "lucide-react"
import { useRouter } from "next/navigation"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface Treatment {
  id: string
  name: string
  cost: number
  mortality: number
  description: string
}

interface HistoryEntry {
  id: string
  timestamp: string
  diagnosis: string
  demographics: {
    ageGroup: string
    race: string
    admissionType: string
    ethnicity: string
    gender: string
  }
  treatments: Treatment[]
  selectedTreatment?: Treatment
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const router = useRouter()
  const [history, setHistory] = React.useState<HistoryEntry[]>([])

  // Load data from localStorage on mount
  React.useEffect(() => {
    const loadStoredData = () => {
      try {
        const storedHistory = localStorage.getItem("treatmentHistory")
        if (storedHistory) {
          setHistory(JSON.parse(storedHistory))
        }
      } catch (error) {
        console.error("Error loading data from localStorage:", error)
      }
    }

    loadStoredData()

    // Listen for storage changes
    const handleStorageChange = () => {
      loadStoredData()
    }

    window.addEventListener("storage", handleStorageChange)
    window.addEventListener("localStorageUpdate", handleStorageChange)

    return () => {
      window.removeEventListener("storage", handleStorageChange)
      window.removeEventListener("localStorageUpdate", handleStorageChange)
    }
  }, [])

  const handleHomeClick = () => {
    try {
      router.push("/")
    } catch (error) {
      console.error("Error clearing localStorage:", error)
    }
  }

  const clearHistory = () => {
    try {
      localStorage.removeItem("treatmentHistory")
      setHistory([])
      window.dispatchEvent(new Event("localStorageUpdate"))
    } catch (error) {
      console.error("Error clearing history:", error)
    }
  }

  const removeHistoryEntry = (entryId: string) => {
    try {
      const newHistory = history.filter((entry) => entry.id !== entryId)
      setHistory(newHistory)
      localStorage.setItem("treatmentHistory", JSON.stringify(newHistory))
      window.dispatchEvent(new Event("localStorageUpdate"))
    } catch (error) {
      console.error("Error removing history entry:", error)
    }
  }

  const formatDemographics = (demographics: HistoryEntry["demographics"]) => {
    const items = []
    if (demographics.ageGroup) items.push(`Age: ${demographics.ageGroup}`)
    if (demographics.gender) items.push(`Gender: ${demographics.gender}`)
    if (demographics.admissionType) items.push(`Admission: ${demographics.admissionType}`)
    return items.join(" • ")
  }

  return (
    <Sidebar {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" onClick={handleHomeClick} className="cursor-pointer">
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                <Home className="size-4" />
              </div>
              <div className="flex flex-col gap-0.5 leading-none">
                <span className="font-semibold">MediCost</span>
                <span className="text-xs text-sidebar-foreground/70">Healthcare Analytics</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="flex items-center justify-between pr-2">
            <div className="flex items-center gap-2">
              <History className="size-4" />
              Treatment History
            </div>
            {history.length > 0 && (
              <Button variant="ghost" size="sm" onClick={clearHistory} className="h-6 w-6 p-0 hover:bg-destructive/20">
                <Trash2 className="h-3 w-3" />
              </Button>
            )}
          </SidebarGroupLabel>
          <SidebarGroupContent>
            {history.length === 0 ? (
              <div className="px-2 py-4 text-center">
                <div className="text-sm text-sidebar-foreground/50 italic">No treatment history yet</div>
                <div className="text-xs text-sidebar-foreground/40 mt-1">Select treatments to see them here</div>
              </div>
            ) : (
              <ScrollArea className="h-[calc(100vh-200px)] px-2">
                <div className="space-y-3">
                  {history.map((entry, index) => (
                    <div
                      key={entry.id}
                      className="border border-sidebar-border rounded-lg p-3 space-y-2 bg-sidebar-accent/20 hover:bg-sidebar-accent/30 transition-colors  w-55"
                    >
                      {/* Header with diagnosis and date */}
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-sidebar-foreground truncate">{entry.diagnosis}</div>
                          <div className="flex items-center gap-1 text-xs text-sidebar-foreground/60 mt-1">
                            <Calendar className="h-3 w-3" />
                            {new Date(entry.timestamp).toLocaleDateString()}
                          </div>
                        </div>
                        <div className="flex items-center gap-1 flex-shrink-0">
                          <Badge variant="outline" className="text-xs">
                            #{history.length - index}
                          </Badge>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeHistoryEntry(entry.id)}
                            className="h-6 w-6 p-0 hover:bg-destructive/20 flex-shrink-0"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>

                      {/* Demographics summary */}
                      {formatDemographics(entry.demographics) && (
                        <div className="text-xs text-sidebar-foreground/50 border-l-2 border-sidebar-border pl-2">
                          {formatDemographics(entry.demographics)}
                        </div>
                      )}

                      {/* Selected treatment */}
                      {entry.selectedTreatment && (
                        <div className="bg-sidebar-accent/40 rounded-md p-2 space-y-1">
                          <div className="text-xs font-medium text-green-400">✓ Selected Treatment</div>
                          <div className="text-sm font-medium text-sidebar-foreground">
                            {entry.selectedTreatment.name}
                          </div>
                          <div className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-1 text-green-400">
                              <DollarSign className="h-3 w-3" />${entry.selectedTreatment.cost.toLocaleString()}
                            </div>
                            <div className="flex items-center gap-1 text-orange-400">
                              <AlertTriangle className="h-3 w-3" />
                              {entry.selectedTreatment.mortality}%
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </ScrollArea>
            )}
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarRail />
    </Sidebar>
  )
}
