import Link from "next/link";
import { Contact } from "@/components/ui/Contact";
import { SITE } from "@/lib/site";

export const metadata = { title: "About" };

export default function AboutPage() {
  return (
    <>
      <h1>About SCROLL</h1>
      <p>
        SCROLL brings publicly available posts and videos from several social platforms into one vertical feed, and lets you keep your saves from every platform in one
        place. It is operated by {SITE.operator}.
      </p>

      <h2>How content works</h2>
      <ul>
        <li>
          Everything you watch in SCROLL is played by the <strong>official embedded player or widget</strong> of the original platform (YouTube, TikTok, Instagram, X,
          Reddit). SCROLL never downloads, copies, re-hosts or alters the media.
        </li>
        <li>Each item shows its original platform and links back to the original publication.</li>
        <li>If a creator or platform removes or restricts a publication, it stops being playable in SCROLL too.</li>
        <li>
          No platform gives third-party apps access to its personalized recommendations. The &quot;For you&quot; feed is SCROLL&apos;s own ranking, based only on what you
          do inside SCROLL.
        </li>
      </ul>

      <h2>What is supported</h2>
      <p>
        The Discover and Profile screens list, for each platform, exactly what is available on this deployment: pasting a public link, a discovery feed, search and
        autoplay. Features that a platform does not officially allow are shown as unavailable.
      </p>

      <h2>Independence</h2>
      <p>
        SCROLL is an independent service. It is not affiliated with, endorsed by or sponsored by YouTube, Google, TikTok, Instagram, Meta, X or Reddit. Their names and
        logos are trademarks of their respective owners and are used only to identify the source of content.
      </p>

      <h2>Creators and rights holders</h2>
      <p>
        Content is displayed through each platform&apos;s official embed, under that platform&apos;s terms. To stop a publication from appearing in embeds, use the embed
        or privacy settings of the original platform; the change applies to SCROLL automatically. To ask us to remove a link from SCROLL&apos;s own catalog, write to{" "}
        <Contact /> with the link concerned. We act on valid requests promptly.
      </p>

      <h2>More</h2>
      <p>
        <Link href="/legal/privacy">Privacy policy</Link> · <Link href="/legal/terms">Terms of use</Link>
      </p>
    </>
  );
}
