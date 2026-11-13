import { Suspense } from "react";
import { DiscoverScreen } from "@/components/discover/DiscoverScreen";

export const metadata = { title: "Discover" };

export default function DiscoverPage() {
  return (
    <Suspense fallback={<div className="min-h-dvh" />}>
      <DiscoverScreen />
    </Suspense>
  );
}
