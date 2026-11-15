import { SITE } from "@/lib/site";

/** Contact line for legal pages. The address is set per deployment (NEXT_PUBLIC_CONTACT_EMAIL). */
export function Contact() {
  if (!SITE.contactEmail) {
    return <span>the contact address published on this page before public launch (not configured on this deployment yet)</span>;
  }
  return <a href={`mailto:${SITE.contactEmail}`}>{SITE.contactEmail}</a>;
}
