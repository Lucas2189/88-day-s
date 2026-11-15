import { StatusScreen } from "@/components/ui/StatusScreen";

export const metadata = { title: "Offline" };

export default function OfflinePage() {
  return <StatusScreen title="offline.title" body="offline.body" action="common.retry" />;
}
