import { Suspense } from "react";
import { ProfileScreen } from "@/components/profile/ProfileScreen";

export const metadata = { title: "Profile" };

export default function ProfilePage() {
  return (
    <Suspense fallback={<div className="min-h-dvh" />}>
      <ProfileScreen />
    </Suspense>
  );
}
