import { type NextRequest, NextResponse } from "next/server"

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

export async function POST(request: NextRequest) {
  try {
    const data: DiagnosisData = await request.json()

    // Call your Python FastAPI backend
    const response = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        Diagnosis_Code: data.diagnosis,
        Age_Group: data.ageGroup,
        Gender: data.gender,
        Race: data.race,
        Ethnicity: data.ethnicity,
        Type_of_Admission: data.admissionType,
      }),
    })

    const prediction = await response.json()

    console.log("Prediction response:", prediction)

    if (!response.ok || prediction.error) {
      throw new Error(prediction.error || "Backend returned error")
    }

    const allTreatments: Treatment [] = []

   for (let i = 0; i < prediction.length; i++) {
      allTreatments.push({
        id: `${data.diagnosis}-predicted-treatment`,
        name: "Procedure: " + prediction[i].procedure_code,
        cost: prediction[i].total_costs,
        mortality: prediction[i].mortality,
        description: "Treatment plan based on predicted outcomes for the given diagnosis and patient demographics.",
        stay: prediction[i].length_of_stay,
      })

    }

    return NextResponse.json({
      treatments: allTreatments,
      message: "Prediction retrieved successfully",
      demographics: data,
    })
  } catch (error) {
    console.error("Error processing treatment request:", error)
    return NextResponse.json(
        { error: "Failed to process treatment request" },
        { status: 500 }
    )
  }
}
