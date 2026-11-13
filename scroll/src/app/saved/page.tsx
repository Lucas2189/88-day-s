import { Suspense } from "react";
import { SavedScreen } from "@/components/saved/SavedScreen";

export const metadata = { title: "Saved" };

export default function SavedPage() {
  return (
    <Suspense fallback={<div className="min-h-dvh" />}>
      <SavedScreen />
    </Suspense>
  );
}
