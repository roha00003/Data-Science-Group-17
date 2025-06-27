"use client"

import * as React from "react"
import { Check, ChevronsUpDown, Loader2, Activity, DollarSign, AlertTriangle, RotateCcw, Info } from "lucide-react"

import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface DiagnosisData {
  diagnosis: string
  ageGroup: string
  race: string
  admissionType: string
  ethnicity: string
  gender: string
}

interface Treatment {
  id: string
  name: string
  cost: number
  mortality: number
  description: string
  stay: number
}

interface HistoryEntry {
  id: string
  timestamp: string
  diagnosis: string
  demographics: Omit<DiagnosisData, "diagnosis">
  treatments: Treatment[]
  selectedTreatment?: Treatment
}

const diagnoses = [
  "Acute Myocardial Infarction",
  "Pneumonia",
  "Diabetes Mellitus Type 2",
  "Hypertension",
  "Chronic Obstructive Pulmonary Disease",
  "Stroke",
  "Heart Failure",
  "Sepsis",
  "Kidney Disease",
  "Cancer",
  "Asthma",
  "Chronic Kidney Disease",
  "Atrial Fibrillation",
  "Depression",
  "Osteoarthritis",
]

const demographicOptions = {
  ageGroup: ["0–17", "18–29", "30–49", "50–69", "70+"],
  race: ["White", "Black or African American", "Asian", "Hispanic or Latino", "Native American", "Other"],
  admissionType: ["Emergency", "Urgent", "Elective", "Newborn", "Trauma", "Not Available"],
  ethnicity: ["Spanish/Hispanic", "Not Span/Hispanic", "Multi-ethnic", "Unknown"],
  gender: ["Male", "Female", "Other"],
}

const initialDiagnosisData: DiagnosisData = {
  diagnosis: "",
  ageGroup: "",
  race: "",
  admissionType: "",
  ethnicity: "",
  gender: "",
}

export function DiagnosisForm() {
  const [diagnosisData, setDiagnosisData] = React.useState<DiagnosisData>(initialDiagnosisData)
  const [treatments, setTreatments] = React.useState<Treatment[]>([])
  const [isLoading, setIsLoading] = React.useState(false)
  const [openDiagnosis, setOpenDiagnosis] = React.useState(false)
  const [hasSelectedTreatment, setHasSelectedTreatment] = React.useState(false)
  const [diagnoses, setDiagnoses] = React.useState<string[]>([])

  // Load diagnosis data from public txt file
  React.useEffect(() => {
    fetch('/diagnosen_beschreibung.txt')
        .then(res => res.text())
        .then(data => {
          const diagData = data
              .split('\n')
              .map((line) => line.split('\n')
                .filter((item) => item.trim() !== "")) // Filter out empty lines
          setDiagnoses(diagData)
        })
        .catch(err => console.error(err))
  }, [])


  // Load data from localStorage on mount
  React.useEffect(() => {
    const loadStoredData = () => {
      try {
        const storedData = {
          diagnosis: localStorage.getItem("diagnosis") || "",
          ageGroup: localStorage.getItem("ageGroup") || "",
          race: localStorage.getItem("race") || "",
          admissionType: localStorage.getItem("admissionType") || "",
          ethnicity: localStorage.getItem("ethnicity") || "",
          gender: localStorage.getItem("gender") || "",
        }
        setDiagnosisData(storedData)
      } catch (error) {
        console.error("Error loading data from localStorage:", error)
      }
    }

    loadStoredData()

    // Listen for clear all event from sidebar
    const handleClearAll = () => {
      setDiagnosisData(initialDiagnosisData)
      setTreatments([])
      setHasSelectedTreatment(false)
    }

    window.addEventListener("clearAll", handleClearAll)

    return () => {
      window.removeEventListener("clearAll", handleClearAll)
    }
  }, [])

  const updateDiagnosisData = (key: keyof DiagnosisData, value: string) => {
    const newData = { ...diagnosisData, [key]: value }
    setDiagnosisData(newData)
    localStorage.setItem(key, value)
    window.dispatchEvent(new Event("localStorageUpdate"))
  }

  const getTreatmentRecommendations = async () => {
    if (!diagnosisData.diagnosis) return

    setIsLoading(true)
    try {
      const response = await fetch("/api/treatments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(diagnosisData),
      })

      if (response.ok) {
        const data = await response.json()
        setTreatments(data.treatments)
      }
    } catch (error) {
      console.error("Error fetching treatments:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const selectTreatment = (treatment: Treatment) => {
    // Get current history from localStorage to avoid overwriting deletions
    const currentHistory = JSON.parse(localStorage.getItem("treatmentHistory") || "[]")

    const historyEntry: HistoryEntry = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      diagnosis: diagnosisData.diagnosis,
      demographics: {
        ageGroup: diagnosisData.ageGroup,
        race: diagnosisData.race,
        admissionType: diagnosisData.admissionType,
        ethnicity: diagnosisData.ethnicity,
        gender: diagnosisData.gender,
      },
      treatments,
      selectedTreatment: treatment,
    }

    const newHistory = [historyEntry, ...currentHistory]
    localStorage.setItem("treatmentHistory", JSON.stringify(newHistory))
    window.dispatchEvent(new Event("localStorageUpdate"))

    setHasSelectedTreatment(true)
  }

  const startOver = () => {
    // Clear form data
    setDiagnosisData(initialDiagnosisData)
    setTreatments([])
    setHasSelectedTreatment(false)

    // Clear localStorage form data but keep history
    Object.keys(initialDiagnosisData).forEach((key) => {
      localStorage.removeItem(key)
    })

    window.dispatchEvent(new Event("localStorageUpdate"))
  }

  const canGetTreatments = diagnosisData.diagnosis.length > 0

  return (
    <div className="space-y-6">
      {/* Start Over Button - appears after treatment selection */}
      {hasSelectedTreatment && (
        <Card className="border-green-500/20 bg-green-500/5">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-green-400">Treatment Selected Successfully!</h3>
                <p className="text-sm text-muted-foreground">Your selection has been added to the treatment history.</p>
              </div>
              <Button onClick={startOver} variant="outline" className="flex items-center gap-2">
                <RotateCcw className="h-4 w-4" />
                Start New Analysis
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Selection Summary */}
      <Card className="border-border bg-card/50">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Current Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 text-sm">
            <div>
              <div className="text-muted-foreground text-xs">Diagnosis</div>
              <div className="font-medium">{diagnosisData.diagnosis || "Not selected"}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs">Age Group</div>
              <div className="font-medium">{diagnosisData.ageGroup || "Not specified"}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs">Gender</div>
              <div className="font-medium">{diagnosisData.gender || "Not specified"}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs">Race</div>
              <div className="font-medium">{diagnosisData.race || "Not specified"}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs">Admission</div>
              <div className="font-medium">{diagnosisData.admissionType || "Not specified"}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs">Ethnicity</div>
              <div className="font-medium">{diagnosisData.ethnicity || "Not specified"}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Diagnosis Selection */}
      <Card className="border-border bg-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Diagnosis Selection
          </CardTitle>
          <CardDescription>Select the primary diagnosis for treatment recommendations</CardDescription>
        </CardHeader>
        <CardContent>
          <Popover open={openDiagnosis} onOpenChange={setOpenDiagnosis}>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                role="combobox"
                aria-expanded={openDiagnosis}
                className="w-full justify-between bg-background"
              >
                {diagnosisData.diagnosis || "Select diagnosis..."}
                <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-full p-0">
              <Command>
                <CommandInput placeholder="Search diagnosis..." />
                <CommandList>
                  <CommandEmpty>No diagnosis found.</CommandEmpty>
                  <CommandGroup>
                    {diagnoses.map((diagnosis) => (
                      <CommandItem
                        key={diagnosis}
                        value={diagnosis}
                        onSelect={(currentValue) => {
                          updateDiagnosisData("diagnosis", currentValue === diagnosisData.diagnosis ? "" : currentValue)
                          setOpenDiagnosis(false)
                          setTreatments([]) // Clear treatments when diagnosis changes
                          setHasSelectedTreatment(false) // Reset treatment selection state
                        }}
                      >
                        <Check
                          className={cn(
                            "mr-2 h-4 w-4",
                            diagnosisData.diagnosis === diagnosis ? "opacity-100" : "opacity-0",
                          )}
                        />
                        {diagnosis}
                      </CommandItem>
                    ))}
                  </CommandGroup>
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>
        </CardContent>
      </Card>

      {/* Demographics */}
      <Card className="border-border bg-card">
        <CardHeader>
          <CardTitle>Demographics</CardTitle>
          <CardDescription>
            Select demographic information to improve treatment precision (all fields are optional)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(demographicOptions).map(([key, options]) => (
              <div key={key} className="flex flex-col gap-2">
                <label className="text-sm font-medium capitalize">{key.replace(/([A-Z])/g, " $1").trim()}</label>
                <Select
                  value={diagnosisData[key as keyof DiagnosisData]}
                  onValueChange={(value) => {
                    updateDiagnosisData(key as keyof DiagnosisData, value)
                    setTreatments([]) // Clear treatments when demographics change
                    setHasSelectedTreatment(false) // Reset treatment selection state
                  }}
                >
                  <SelectTrigger className="bg-background">
                    <SelectValue placeholder="Select..." />
                  </SelectTrigger>
                  <SelectContent>
                    {options.map((option) => (
                      <SelectItem key={option} value={option}>
                        {option}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Treatment Recommendations */}
      {canGetTreatments && (
        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle>Treatment Recommendations</CardTitle>
            <CardDescription>Get personalized treatment options based on your selections</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button onClick={getTreatmentRecommendations} disabled={isLoading} className="w-full">
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing diagnosis and demographics...
                </>
              ) : (
                "Get Treatment Recommendations"
              )}
            </Button>

            {treatments.length > 0 && (
              <div className="grid gap-4">
                <h3 className="text-lg font-semibold">Recommended Treatments (sorted by cost, then mortality)</h3>
                {treatments.map((treatment, index) => (
                  <Card key={treatment.id} className="border-2 bg-card/50">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-semibold text-lg">{treatment.name}</h4>
                            <Badge variant={index === 0 ? "default" : "secondary"} className="ml-2">
                              Rank #{index + 1}
                            </Badge>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center gap-1 text-2xl font-bold text-green-400 mb-1">
                            <DollarSign className="h-5 w-5" />
                            {treatment.cost.toLocaleString()}
                          </div>
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <AlertTriangle className="h-4 w-4" />
                            Mortality: {treatment.mortality}%
                          </div>
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <Info className="h-4 w-4" />
                            Length of Stay: {treatment.stay} weeks
                          </div>
                        </div>
                      </div>
                      <p className="text-muted-foreground mb-4">{treatment.description}</p>
                      <Button onClick={() => selectTreatment(treatment)} className="w-full">
                        Select This Treatment
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
