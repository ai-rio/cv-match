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

export default function DesignSystemPage() {
  return (
    <div className="container max-w-6xl py-12 space-y-16">
      {/* Header */}
      <section className="text-center space-y-4">
        <H1>Design System Test</H1>
        <Lead>Comprehensive test of typography and color system for CV-Match</Lead>
      </section>

      {/* Typography System */}
      <section className="space-y-8">
        <H2>Typography System</H2>

        {/* Font Families */}
        <div className="space-y-6">
          <H3>Font Families</H3>
          <div className="grid gap-6 md:grid-cols-3">
            <div className="p-6 border rounded-lg">
              <Small className="block mb-2">Plus Jakarta Sans (Sans-Serif)</Small>
              <p className="font-sans text-2xl">The quick brown fox jumps over the lazy dog</p>
              <P className="mt-2">Used for body text, UI elements, navigation, and forms.</P>
            </div>
            <div className="p-6 border rounded-lg">
              <Small className="block mb-2">Source Serif 4 (Serif)</Small>
              <p className="font-serif text-2xl">The quick brown fox jumps over the lazy dog</p>
              <P className="mt-2">Used for hero headlines, marketing copy, and emphasis.</P>
            </div>
            <div className="p-6 border rounded-lg">
              <Small className="block mb-2">JetBrains Mono (Monospace)</Small>
              <p className="font-mono text-2xl">The quick brown fox jumps over the lazy dog</p>
              <P className="mt-2">Used for code snippets, technical data, and match scores.</P>
            </div>
          </div>
        </div>

        {/* Type Scale */}
        <div className="space-y-6">
          <H3>Type Scale</H3>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground w-20">6xl</span>
              <span className="font-serif text-6xl font-bold">Aa</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground w-20">5xl</span>
              <span className="font-serif text-5xl font-bold">Aa</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground w-20">4xl</span>
              <span className="font-serif text-4xl font-bold">Aa</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground w-20">3xl</span>
              <span className="font-sans text-3xl font-semibold">Aa</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground w-20">2xl</span>
              <span className="font-sans text-2xl font-semibold">Aa</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground w-20">xl</span>
              <span className="font-sans text-xl font-semibold">Aa</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground w-20">lg</span>
              <span className="font-sans text-lg">Aa</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground w-20">base</span>
              <span className="font-sans text-base">Aa</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground w-20">sm</span>
              <span className="font-sans text-sm">Aa</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground w-20">xs</span>
              <span className="font-sans text-xs">Aa</span>
            </div>
          </div>
        </div>

        {/* Font Weights */}
        <div className="space-y-6">
          <H3>Font Weights</H3>
          <div className="space-y-2">
            <p className="font-sans text-lg font-normal">Normal (400) - Regular body text</p>
            <p className="font-sans text-lg font-medium">Medium (500) - Emphasized text</p>
            <p className="font-sans text-lg font-semibold">Semibold (600) - Subheadings</p>
            <p className="font-sans text-lg font-bold">Bold (700) - Headings</p>
          </div>
        </div>

        {/* Typography Components */}
        <div className="space-y-6">
          <H3>Typography Components</H3>
          <div className="space-y-4">
            <div>
              <Small>H1 Component</Small>
              <H1>Hero Headline with Source Serif 4</H1>
            </div>
            <div>
              <Small>H2 Component</Small>
              <H2>Section Header with Plus Jakarta Sans</H2>
            </div>
            <div>
              <Small>H3 Component</Small>
              <H3>Subsection Header</H3>
            </div>
            <div>
              <Small>H4 Component</Small>
              <H4>Card Title</H4>
            </div>
            <div>
              <Small>Paragraph Component</Small>
              <P>
                This is regular paragraph text using Plus Jakarta Sans. It should be highly readable
                at 16px (1rem) with a line height of 1.5. The font is optimized for body copy and UI
                elements.
              </P>
            </div>
            <div>
              <Small>Lead Component</Small>
              <Lead>
                This is lead text - slightly larger and used for introductions or emphasis.
              </Lead>
            </div>
            <div>
              <Small>Muted Component</Small>
              <Muted>This is muted text - secondary information.</Muted>
            </div>
            <div>
              <Small>Small Component</Small>
              <Small>This is small text - fine print and captions.</Small>
            </div>
            <div>
              <Small>Code Component</Small>
              <P>
                Inline code: <Code>const theme = 'dark'</Code>
              </P>
            </div>
            <div>
              <Small>Blockquote Component</Small>
              <Blockquote>
                "Depois de otimizar, consegui 3 entrevistas em uma semana!" — Maria S.,
                Desenvolvedora Senior
              </Blockquote>
            </div>
          </div>
        </div>
      </section>

      {/* Color System */}
      <section className="space-y-8">
        <H2>Color System</H2>

        {/* Primary Colors */}
        <div className="space-y-6">
          <H3>Semantic Colors</H3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-2">
              <div className="h-20 bg-primary rounded-lg"></div>
              <Small>Primary</Small>
              <Code>bg-primary</Code>
            </div>
            <div className="space-y-2">
              <div className="h-20 bg-secondary rounded-lg"></div>
              <Small>Secondary</Small>
              <Code>bg-secondary</Code>
            </div>
            <div className="space-y-2">
              <div className="h-20 bg-accent rounded-lg"></div>
              <Small>Accent</Small>
              <Code>bg-accent</Code>
            </div>
            <div className="space-y-2">
              <div className="h-20 bg-muted rounded-lg"></div>
              <Small>Muted</Small>
              <Code>bg-muted</Code>
            </div>
            <div className="space-y-2">
              <div className="h-20 bg-success rounded-lg"></div>
              <Small>Success</Small>
              <Code>bg-success</Code>
            </div>
            <div className="space-y-2">
              <div className="h-20 bg-warning rounded-lg"></div>
              <Small>Warning</Small>
              <Code>bg-warning</Code>
            </div>
            <div className="space-y-2">
              <div className="h-20 bg-info rounded-lg"></div>
              <Small>Info</Small>
              <Code>bg-info</Code>
            </div>
            <div className="space-y-2">
              <div className="h-20 bg-destructive rounded-lg"></div>
              <Small>Destructive</Small>
              <Code>bg-destructive</Code>
            </div>
          </div>
        </div>

        {/* Text Colors */}
        <div className="space-y-6">
          <H3>Text Colors</H3>
          <div className="space-y-2 p-6 bg-card rounded-lg border">
            <P className="text-foreground">Foreground text (default)</P>
            <P className="text-muted-foreground">Muted text (secondary)</P>
            <P className="text-primary">Primary text</P>
            <P className="text-secondary">Secondary text</P>
            <P className="text-accent">Accent text</P>
            <P className="text-success">Success text</P>
            <P className="text-warning">Warning text</P>
            <P className="text-info">Info text</P>
            <P className="text-destructive">Destructive text</P>
          </div>
        </div>

        {/* Border Colors */}
        <div className="space-y-6">
          <H3>Border Colors</H3>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="p-4 border-2 border-border rounded-lg">
              <Small>Default Border</Small>
            </div>
            <div className="p-4 border-2 border-primary rounded-lg">
              <Small>Primary Border</Small>
            </div>
            <div className="p-4 border-2 border-input rounded-lg">
              <Small>Input Border</Small>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Elements */}
      <section className="space-y-8">
        <H2>Interactive Elements</H2>

        <div className="space-y-6">
          <H3>Buttons</H3>
          <div className="flex flex-wrap gap-4">
            <button className="btn btn-primary">Primary Button</button>
            <button className="btn btn-secondary">Secondary Button</button>
            <button className="btn btn-success">Success Button</button>
            <button className="btn btn-warning">Warning Button</button>
            <button className="btn btn-info">Info Button</button>
            <button className="btn btn-destructive">Destructive Button</button>
          </div>
        </div>

        <div className="space-y-6">
          <H3>Form Elements</H3>
          <div className="space-y-4 max-w-md">
            <input type="text" placeholder="Text input" className="input w-full" />
            <input type="email" placeholder="Email input" className="input w-full" />
            <textarea placeholder="Textarea" className="input w-full h-24 resize-none"></textarea>
          </div>
        </div>
      </section>

      {/* Theme Testing */}
      <section className="space-y-8">
        <H2>Theme Testing</H2>
        <P>
          This design system should work seamlessly in both light and dark themes. Use the theme
          toggle in the navigation to switch between themes and verify all colors and typography
          remain readable and accessible.
        </P>

        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4 p-6 bg-card rounded-lg border">
            <H3>Light Theme Elements</H3>
            <P>Text should be dark on light backgrounds.</P>
            <div className="h-20 bg-primary rounded"></div>
            <button className="btn btn-primary">Primary Button</button>
          </div>
          <div className="space-y-4 p-6 bg-card rounded-lg border">
            <H3>Dark Theme Elements</H3>
            <P>Text should be light on dark backgrounds.</P>
            <div className="h-20 bg-primary rounded"></div>
            <button className="btn btn-primary">Primary Button</button>
          </div>
        </div>
      </section>
    </div>
  );
}
