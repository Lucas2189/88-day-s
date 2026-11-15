import { Contact } from "@/components/ui/Contact";
import { SITE } from "@/lib/site";

export const metadata = { title: "Privacy policy" };

export default function PrivacyPage() {
  return (
    <>
      <h1>Privacy policy</h1>
      <p>Last updated: {SITE.legalUpdated}</p>
      <p>
        This policy explains what information SCROLL handles, why, and the choices you have. SCROLL is operated by {SITE.operator} (&quot;we&quot;). Contact: <Contact />.
      </p>

      <h2>1. Information stored on your device</h2>
      <p>By default SCROLL works without an account. The following stays in your browser&apos;s local storage on your device:</p>
      <ul>
        <li>your preferences (language, content region, interests, enabled platforms, playback settings);</li>
        <li>your bookmarks, collections, likes and hidden items;</li>
        <li>links you add, with their public metadata (title, author name, thumbnail address);</li>
        <li>usage signals used to rank your feed (for example that an item was viewed, skipped or saved, and for how long it was on screen).</li>
      </ul>
      <p>You can export or delete all of it at any time from Profile → Your data.</p>

      <h2>2. Optional account and synchronization</h2>
      <p>
        If account sign-in is enabled on this deployment and you choose to sign in, we process your email address to authenticate you, and we store the information
        listed in section 1 on our database provider (Supabase) so that it follows you across devices. Each account can only read and write its own rows. You can ask
        us to delete your account and its data at any time.
      </p>

      <h2>3. Information processed by our servers</h2>
      <ul>
        <li>
          <strong>Links you submit and search terms</strong> are sent to our server so it can request public metadata from the platform&apos;s official endpoints. They
          are not linked to an identity and are kept only in a short-lived cache.
        </li>
        <li>
          <strong>Technical data</strong> such as your IP address is processed transiently to deliver the service and to limit abusive request rates. Our hosting
          provider may keep standard server logs.
        </li>
        <li>
          <strong>Audience measurement</strong>: where enabled, we use a cookieless analytics service (Vercel Web Analytics) that records page views and a small set of
          anonymous events (for example &quot;an item was saved&quot;). It does not use cookies and does not identify you across sites.
        </li>
      </ul>

      <h2>4. Third-party platforms</h2>
      <p>
        Content is played by the embedded players and widgets of the original platforms. When an embed loads, that platform receives technical information such as your
        IP address and may set its own cookies or recognize you if you are signed in to it, under its own privacy policy:
      </p>
      <ul>
        <li>
          YouTube: SCROLL uses YouTube API Services. See the{" "}
          <a href="https://www.google.com/policies/privacy" target="_blank" rel="noopener noreferrer">
            Google Privacy Policy
          </a>
          .
        </li>
        <li>
          TikTok:{" "}
          <a href="https://www.tiktok.com/legal/privacy-policy" target="_blank" rel="noopener noreferrer">
            TikTok Privacy Policy
          </a>
          .
        </li>
        <li>
          Instagram:{" "}
          <a href="https://privacycenter.instagram.com/policy" target="_blank" rel="noopener noreferrer">
            Meta Privacy Policy
          </a>
          .
        </li>
        <li>
          X:{" "}
          <a href="https://x.com/privacy" target="_blank" rel="noopener noreferrer">
            X Privacy Policy
          </a>
          .
        </li>
        <li>
          Reddit:{" "}
          <a href="https://www.reddit.com/policies/privacy-policy" target="_blank" rel="noopener noreferrer">
            Reddit Privacy Policy
          </a>
          .
        </li>
      </ul>
      <p>
        SCROLL does not access your accounts on those platforms and receives no information about your activity there. You can disable any platform in Profile → Sources;
        its embeds are then no longer loaded.
      </p>

      <h2>5. What we do not do</h2>
      <ul>
        <li>We do not sell personal information.</li>
        <li>We do not download or store videos, images or other media from the platforms.</li>
        <li>We do not build advertising profiles.</li>
      </ul>

      <h2>6. Retention</h2>
      <p>
        Data on your device stays until you delete it or clear your browser data. Account data is kept until you delete your account. Server caches of public metadata
        expire automatically within hours.
      </p>

      <h2>7. Your rights</h2>
      <p>
        Depending on where you live, you may have the right to access, correct, export or delete your personal information, and to object to or restrict certain
        processing. To exercise these rights, contact us at <Contact />. You may also lodge a complaint with your local data protection authority.
      </p>

      <h2>8. Children</h2>
      <p>
        SCROLL is not directed to children under 13, or under the minimum age required by the platforms whose content is displayed in your country. Do not use SCROLL if
        you are below that age.
      </p>

      <h2>9. Changes</h2>
      <p>We may update this policy. The date at the top shows the latest version. Significant changes will be announced in the app.</p>
    </>
  );
}
