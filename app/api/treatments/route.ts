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
        CCSR_Procedure_Code: data.diagnosis,
        Age_Group: data.ageGroup,
        Gender: data.gender,
        Race: data.race,
        Ethnicity: data.ethnicity,
      }),
    })

    const prediction = await response.json()

    if (!response.ok || prediction.error) {
      throw new Error(prediction.error || "Backend returned error")
    }

    // Create treatment object from backend prediction
    const treatment: Treatment = {
      id: `${data.diagnosis}-predicted-treatment`,
      name: "Predicted Personalized Treatment",
      cost: prediction.total_costs,
      mortality: prediction.mortality,
      description: "Treatment plan based on predicted outcomes for the given diagnosis and patient demographics.",
      stay: prediction.length_of_stay,
    }

    return NextResponse.json({
      treatments: [treatment],
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
