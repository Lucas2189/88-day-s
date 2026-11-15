import { Contact } from "@/components/ui/Contact";
import { SITE } from "@/lib/site";

export const metadata = { title: "Terms of use" };

export default function TermsPage() {
  return (
    <>
      <h1>Terms of use</h1>
      <p>Last updated: {SITE.legalUpdated}</p>
      <p>
        These terms govern your use of SCROLL, operated by {SITE.operator} (&quot;we&quot;). By using SCROLL you agree to them. If you do not agree, please do not use the
        service.
      </p>

      <h2>1. The service</h2>
      <p>
        SCROLL lets you discover and organize publicly available posts and videos from third-party platforms. Content is displayed through each platform&apos;s official
        embedded player or widget. SCROLL does not host that content and does not control it.
      </p>

      <h2>2. Third-party platform terms</h2>
      <p>Because content is played by the platforms themselves, their terms also apply when you watch it in SCROLL:</p>
      <ul>
        <li>
          SCROLL uses YouTube API Services. By using SCROLL you agree to be bound by the{" "}
          <a href="https://www.youtube.com/t/terms" target="_blank" rel="noopener noreferrer">
            YouTube Terms of Service
          </a>
          .
        </li>
        <li>
          <a href="https://www.tiktok.com/legal/terms-of-service" target="_blank" rel="noopener noreferrer">
            TikTok Terms of Service
          </a>
          ,{" "}
          <a href="https://help.instagram.com/581066165581870" target="_blank" rel="noopener noreferrer">
            Instagram Terms of Use
          </a>
          ,{" "}
          <a href="https://x.com/tos" target="_blank" rel="noopener noreferrer">
            X Terms of Service
          </a>{" "}
          and{" "}
          <a href="https://www.redditinc.com/policies/user-agreement" target="_blank" rel="noopener noreferrer">
            Reddit User Agreement
          </a>
          .
        </li>
      </ul>

      <h2>3. Acceptable use</h2>
      <ul>
        <li>Only add links to content that is public and that you are allowed to share.</li>
        <li>Do not use SCROLL to download, copy, record or redistribute content from the platforms.</li>
        <li>Do not try to bypass platform restrictions, age gates or regional limits.</li>
        <li>Do not use automated tools to send requests to SCROLL, and do not interfere with its operation or security.</li>
        <li>Do not add links to unlawful content. We may remove any link from our catalog and restrict access in case of abuse.</li>
      </ul>

      <h2>4. Content ownership</h2>
      <p>
        All posts, videos, names and logos displayed from the platforms belong to their creators and owners. SCROLL claims no rights over them. Rights holders can
        contact us at <Contact /> to have a link removed from SCROLL&apos;s catalog.
      </p>

      <h2>5. Your account and data</h2>
      <p>
        SCROLL can be used without an account. If you create one, keep your sign-in email secure. You can export or delete your data at any time, as described in the
        Privacy policy.
      </p>

      <h2>6. Availability</h2>
      <p>
        The service depends on third-party platforms that may change or withdraw their embedding features at any time. We therefore provide SCROLL &quot;as is&quot;,
        without guarantee that any particular platform, content or feature will remain available.
      </p>

      <h2>7. Liability</h2>
      <p>
        To the extent permitted by law, we are not liable for the content published on third-party platforms, nor for indirect or consequential damages arising from the
        use of SCROLL. Nothing in these terms limits rights that cannot be limited under the consumer law that applies to you.
      </p>

      <h2>8. Changes and contact</h2>
      <p>
        We may update these terms; the date at the top shows the latest version. Continued use after a change means you accept the new terms. Questions: <Contact />.
      </p>
    </>
  );
}
