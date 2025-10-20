/**
 * Component Playground Page for CV-Match Phase 0.8
 *
 * Brazilian market optimized component showcase
 * WCAG 2.1 AA compliant with excellent accessibility
 *
 * Features:
 * - All shadcn/ui components showcase
 * - Brazilian market patterns
 * - Interactive examples
 * - Accessibility demonstrations
 */

import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';

import {
  Alert,
  AlertDescription,
  AlertTitle,
  Avatar,
  AvatarGroup,
  AvatarWithStatus,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Checkbox,
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Form,
  FormField,
  FormSubmit,
  Input,
  Progress,
  RadioGroup,
  RadioGroupItem,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Separator,
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  Skeleton,
  SkeletonCard,
  SkeletonList,
  SkeletonTable,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Textarea,
  ToastProvider,
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui';

export const metadata: Metadata = {
  title: 'Component Playground - CV-Match',
  description: 'Interactive showcase of all UI components',
};

export default async function ComponentsPage() {
  const t = await getTranslations('ComponentsPage');

  return (
    <div className="container mx-auto py-8 px-4">
      <ToastProvider>
        <div className="space-y-12">
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">
              {t('title', { defaultValue: 'Component Playground' })}
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              {t('description', {
                defaultValue:
                  'Interactive showcase of all UI components with Brazilian market optimizations',
              })}
            </p>
          </div>

          {/* Buttons Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Buttons</h2>
            <div className="flex flex-wrap gap-4">
              <Button variant="default">Default</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="success">Success</Button>
              <Button variant="warning">Warning</Button>
              <Button variant="info">Info</Button>
              <Button loading>Loading</Button>
              <Button size="sm">Small</Button>
              <Button size="lg">Large</Button>
            </div>
          </section>

          {/* Alerts Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Alerts</h2>
            <div className="space-y-4">
              <Alert>
                <AlertTitle>Information</AlertTitle>
                <AlertDescription>This is an informational alert message.</AlertDescription>
              </Alert>
              <Alert variant="destructive">
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>Something went wrong. Please try again.</AlertDescription>
              </Alert>
            </div>
          </section>

          {/* Badges Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Badges</h2>
            <div className="flex flex-wrap gap-2">
              <Badge>Default</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="outline">Outline</Badge>
              <Badge variant="destructive">Destructive</Badge>
            </div>
          </section>

          {/* Cards Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Cards</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Card Title</CardTitle>
                  <CardDescription>Card Description</CardDescription>
                </CardHeader>
                <CardContent>
                  <p>Card content goes here.</p>
                </CardContent>
                <CardFooter>
                  <Button>Action</Button>
                </CardFooter>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Another Card</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>Different card content.</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Third Card</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>More card content.</p>
                </CardContent>
              </Card>
            </div>
          </section>

          {/* Form Elements Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Form Elements</h2>
            <Card>
              <CardHeader>
                <CardTitle>Sample Form</CardTitle>
                <CardDescription>Interactive form with various elements</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <Form>
                  <FormField name="name" label="Name" description="Enter your full name">
                    <Input placeholder="John Doe" />
                  </FormField>

                  <FormField name="email" label="Email" description="Enter your email address">
                    <Input type="email" placeholder="john@example.com" />
                  </FormField>

                  <FormField name="message" label="Message" description="Tell us something">
                    <Textarea placeholder="Your message here..." rows={3} />
                  </FormField>

                  <FormField name="newsletter" label="Newsletter">
                    <Checkbox label="Subscribe to newsletter" />
                  </FormField>

                  <FormField name="plan" label="Plan">
                    <RadioGroup>
                      <RadioGroupItem value="free" label="Free Plan" />
                      <RadioGroupItem value="pro" label="Pro Plan" />
                      <RadioGroupItem value="enterprise" label="Enterprise" />
                    </RadioGroup>
                  </FormField>

                  <FormField name="country" label="Country">
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a country" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="br">Brazil</SelectItem>
                        <SelectItem value="us">United States</SelectItem>
                        <SelectItem value="uk">United Kingdom</SelectItem>
                      </SelectContent>
                    </Select>
                  </FormField>

                  <FormSubmit>Submit Form</FormSubmit>
                </Form>
              </CardContent>
            </Card>
          </section>

          {/* Avatars Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Avatars</h2>
            <div className="flex flex-wrap gap-6 items-center">
              <Avatar fallback="JD" />
              <Avatar fallback="Maria Silva" />
              <AvatarWithStatus status="online" fallback="Online" />
              <AvatarWithStatus status="away" fallback="Away" />
              <AvatarWithStatus status="busy" fallback="Busy" />
              <AvatarGroup>
                <Avatar fallback="1" />
                <Avatar fallback="2" />
                <Avatar fallback="3" />
                <Avatar fallback="4" />
                <Avatar fallback="5" />
              </AvatarGroup>
            </div>
          </section>

          {/* Progress Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Progress</h2>
            <div className="space-y-4">
              <Progress value={25} />
              <Progress value={50} />
              <Progress value={75} />
              <Progress value={100} />
            </div>
          </section>

          {/* Skeletons Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Skeletons</h2>
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">Basic Skeleton</h3>
                <Skeleton className="h-4 w-[250px]" />
                <Skeleton className="h-4 w-[200px]" />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-4">Skeleton Card</h3>
                <SkeletonCard />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-4">Skeleton Table</h3>
                <SkeletonTable rows={3} columns={4} />
              </div>

              <div>
                <h3 className="text-lg font-medium mb-4">Skeleton List</h3>
                <SkeletonList items={3} />
              </div>
            </div>
          </section>

          {/* Tables Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Tables</h2>
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Role</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell>João Silva</TableCell>
                    <TableCell>joao@example.com</TableCell>
                    <TableCell>
                      <Badge variant="default">Active</Badge>
                    </TableCell>
                    <TableCell>Admin</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Maria Santos</TableCell>
                    <TableCell>maria@example.com</TableCell>
                    <TableCell>
                      <Badge variant="secondary">Pending</Badge>
                    </TableCell>
                    <TableCell>User</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Carlos Oliveira</TableCell>
                    <TableCell>carlos@example.com</TableCell>
                    <TableCell>
                      <Badge variant="destructive">Inactive</Badge>
                    </TableCell>
                    <TableCell>User</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </Card>
          </section>

          {/* Tabs Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Tabs</h2>
            <Tabs defaultValue="account">
              <TabsList>
                <TabsTrigger value="account">Account</TabsTrigger>
                <TabsTrigger value="password">Password</TabsTrigger>
                <TabsTrigger value="notifications">Notifications</TabsTrigger>
              </TabsList>
              <TabsContent value="account" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Account Settings</CardTitle>
                    <CardDescription>Manage your account settings</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p>Account settings content goes here.</p>
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="password" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Password Settings</CardTitle>
                    <CardDescription>Change your password</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p>Password settings content goes here.</p>
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="notifications" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Notification Settings</CardTitle>
                    <CardDescription>Manage your notifications</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p>Notification settings content goes here.</p>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </section>

          {/* Dialog Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Dialog</h2>
            <Dialog>
              <DialogTrigger asChild>
                <Button>Open Dialog</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Dialog Title</DialogTitle>
                  <DialogDescription>
                    This is a dialog description. You can put any content here.
                  </DialogDescription>
                </DialogHeader>
                <div className="py-4">
                  <p>Dialog content goes here.</p>
                </div>
                <DialogFooter>
                  <Button variant="outline">Cancel</Button>
                  <Button>Confirm</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </section>

          {/* Sheet Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Sheet</h2>
            <Sheet>
              <SheetTrigger asChild>
                <Button>Open Sheet</Button>
              </SheetTrigger>
              <SheetContent>
                <SheetHeader>
                  <SheetTitle>Sheet Title</SheetTitle>
                  <SheetDescription>
                    This is a sheet description. Sheets are great for mobile navigation.
                  </SheetDescription>
                </SheetHeader>
                <div className="py-4">
                  <p>Sheet content goes here.</p>
                </div>
                <SheetFooter>
                  <Button variant="outline">Cancel</Button>
                  <Button>Save</Button>
                </SheetFooter>
              </SheetContent>
            </Sheet>
          </section>

          {/* Command Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Command Palette</h2>
            <Command>
              <CommandInput placeholder="Type a command or search..." />
              <CommandList>
                <CommandEmpty>No results found.</CommandEmpty>
                <CommandGroup heading="Suggestions">
                  <CommandItem>Profile</CommandItem>
                  <CommandItem>Settings</CommandItem>
                  <CommandItem>Help</CommandItem>
                </CommandGroup>
              </CommandList>
            </Command>
          </section>

          {/* Tooltips Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Tooltips</h2>
            <div className="flex flex-wrap gap-4">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline">Hover me</Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>This is a tooltip</p>
                </TooltipContent>
              </Tooltip>

              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline">Another tooltip</Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Another tooltip content</p>
                </TooltipContent>
              </Tooltip>
            </div>
          </section>

          {/* Separators Section */}
          <section className="space-y-6">
            <h2 className="text-2xl font-semibold">Separators</h2>
            <div className="space-y-4">
              <Separator />
              <Separator orientation="vertical" className="h-8" />
              <div className="relative">
                <Separator />
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-background px-2 text-xs text-muted-foreground">
                  Section Title
                </div>
              </div>
            </div>
          </section>
        </div>
      </ToastProvider>
    </div>
  );
}
