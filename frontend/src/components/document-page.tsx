import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"

export default function DocumentSheet(){
    <Sheet>
        <SheetContent className="bg-zinc-950 border-l-[1px] border-l-zinc-950">
            <SheetHeader>
            <SheetTitle>Document</SheetTitle>
            <SheetDescription>
                Document Analysis
            </SheetDescription>
            </SheetHeader>
        </SheetContent>
    </Sheet>
}