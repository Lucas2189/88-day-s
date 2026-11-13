import { Suspense } from "react";
import { HomeFeed } from "@/components/feed/HomeFeed";
import { FeedSkeleton } from "@/components/feed/FeedSkeleton";

export default function HomePage() {
  return (
    <Suspense fallback={<FeedSkeleton />}>
      <HomeFeed />
    </Suspense>
  );
}
