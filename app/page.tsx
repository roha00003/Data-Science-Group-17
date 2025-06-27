import { AppSidebar } from "@/components/app-sidebar"
import { DiagnosisForm } from "@/components/diagnosis-form"
import { Breadcrumb, BreadcrumbItem, BreadcrumbList, BreadcrumbPage } from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"

export default function Page() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b border-border px-4 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <SidebarTrigger className="-ml-1" />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbPage>MediCost Dashboard</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 bg-background">
          <div className="max-w-4xl mx-auto w-full">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-foreground mb-2">Healthcare Treatment Analysis</h1>
              <p className="text-muted-foreground">
                Select a diagnosis and demographic information to receive personalized treatment recommendations. Your
                analysis history will be saved in the sidebar for easy reference.
              </p>
            </div>
            <DiagnosisForm />
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
