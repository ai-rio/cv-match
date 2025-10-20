import {
  Blockquote,
  Code,
  H1,
  H2,
  H3,
  H4,
  Lead,
  Muted,
  P,
  Small,
} from '@/components/ui/typography';

export default function TypographyPage() {
  return (
    <div className="container max-w-4xl py-12 space-y-12">
      {/* Hero */}
      <section className="space-y-4">
        <H1>Typography System</H1>
        <Lead>
          Testing the complete typography scale with Plus Jakarta Sans, Source Serif 4, and
          JetBrains Mono.
        </Lead>
      </section>

      {/* Headings */}
      <section className="space-y-4">
        <H2>Heading Hierarchy</H2>
        <div className="space-y-3">
          <H1>H1 - Hero Headlines (Serif)</H1>
          <H2>H2 - Section Headers (Sans)</H2>
          <H3>H3 - Subsection Headers (Sans)</H3>
          <H4>H4 - Card Titles (Sans)</H4>
        </div>
      </section>

      {/* Body Text */}
      <section className="space-y-4">
        <H2>Body Text</H2>
        <P>
          This is regular paragraph text using Plus Jakarta Sans. It should be highly readable at
          16px (1rem) with a line height of 1.5. The font is optimized for body copy and UI
          elements.
        </P>
        <Lead>
          This is lead text - slightly larger and used for introductions or emphasis. Great for
          setting context before diving into details.
        </Lead>
        <Muted>
          This is muted text - used for secondary information that's less important but still
          relevant.
        </Muted>
        <Small>
          This is small text - perfect for fine print, captions, or supplementary information.
        </Small>
      </section>

      {/* Code */}
      <section className="space-y-4">
        <H2>Code & Data</H2>
        <P>
          Inline code looks like this: <Code>const theme = 'dark'</Code> using JetBrains Mono.
        </P>
        <div className="bg-muted p-4 rounded-lg">
          <code className="font-mono text-sm block">
            {`function OptimizeResume() {
  const [score, setScore] = useState(0)
  return <MatchGauge score={score} />
}`}
          </code>
        </div>
      </section>

      {/* Quote */}
      <section className="space-y-4">
        <H2>Quotes</H2>
        <Blockquote>
          "Depois de otimizar, consegui 3 entrevistas em uma semana!" — Maria S., Desenvolvedora
          Senior
        </Blockquote>
      </section>

      {/* Font Samples */}
      <section className="space-y-4">
        <H2>Font Families</H2>
        <div className="space-y-3">
          <div>
            <Small>Plus Jakarta Sans (Sans-Serif)</Small>
            <p className="font-sans text-2xl">The quick brown fox jumps over the lazy dog</p>
          </div>
          <div>
            <Small>Source Serif 4 (Serif)</Small>
            <p className="font-serif text-2xl">The quick brown fox jumps over the lazy dog</p>
          </div>
          <div>
            <Small>JetBrains Mono (Monospace)</Small>
            <p className="font-mono text-2xl">The quick brown fox jumps over the lazy dog</p>
          </div>
        </div>
      </section>

      {/* Weights */}
      <section className="space-y-4">
        <H2>Font Weights</H2>
        <div className="space-y-2">
          <p className="font-sans text-lg font-normal">Normal (400)</p>
          <p className="font-sans text-lg font-medium">Medium (500)</p>
          <p className="font-sans text-lg font-semibold">Semibold (600)</p>
          <p className="font-sans text-lg font-bold">Bold (700)</p>
        </div>
      </section>
    </div>
  );
}
