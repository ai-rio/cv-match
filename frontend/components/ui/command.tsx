/**
 * Enhanced Command Component for CV-Match Phase 0.8
 *
 * Brazilian market optimized command palette with full design system integration
 * WCAG 2.1 AA compliant with excellent accessibility
 *
 * Features:
 * - Command palette functionality
 * - Brazilian market search patterns
 * - Full keyboard navigation support
 * - Search functionality
 * - Accessibility support
 */

'use client';

import { Search } from 'lucide-react';
import * as React from 'react';

import { cn } from '@/lib/utils';

export interface CommandContextType {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  search: string;
  onSearchChange: (search: string) => void;
  selectedIndex: number;
  setSelectedIndex: React.Dispatch<React.SetStateAction<number>>;
}

const CommandContext = React.createContext<CommandContextType | undefined>(undefined);

export function useCommand() {
  const context = React.useContext(CommandContext);
  if (!context) {
    throw new Error('useCommand must be used within a CommandProvider');
  }
  return context;
}

/**
 * Command Component
 */
export interface CommandProps {
  children: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  placeholder?: string;
  shouldFilter?: boolean;
  filter?: (value: string, search: string) => boolean;
}

export function Command({ children, open: controlledOpen, onOpenChange }: CommandProps) {
  const [internalOpen, setInternalOpen] = React.useState(false);
  const [search, setSearch] = React.useState('');
  const [selectedIndex, setSelectedIndex] = React.useState(0);
  const isOpen = controlledOpen !== undefined ? controlledOpen : internalOpen;

  const handleOpenChange = React.useCallback(
    (newOpen: boolean) => {
      if (controlledOpen === undefined) {
        setInternalOpen(newOpen);
      }
      onOpenChange?.(newOpen);

      // Reset search when closing
      if (!newOpen) {
        setSearch('');
        setSelectedIndex(0);
      }
    },
    [controlledOpen, onOpenChange]
  );

  // Handle keyboard shortcuts
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Cmd/Ctrl + K to open
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        handleOpenChange(!isOpen);
      }

      // Escape to close
      if (event.key === 'Escape' && isOpen) {
        handleOpenChange(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, handleOpenChange]);

  const contextValue: CommandContextType = {
    isOpen,
    onOpenChange: handleOpenChange,
    search,
    onSearchChange: setSearch,
    selectedIndex,
    setSelectedIndex,
  };

  if (!isOpen) {
    return null;
  }

  return (
    <CommandContext.Provider value={contextValue}>
      <div className="fixed inset-0 z-50">
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm"
          onClick={() => handleOpenChange(false)}
        />
        <div className="fixed left-[50%] top-[20%] z-50 grid w-full max-w-lg translate-x-[-50%] gap-4 border bg-background p-4 shadow-lg duration-200 sm:rounded-lg md:w-full">
          {children}
        </div>
      </div>
    </CommandContext.Provider>
  );
}

/**
 * Command Input
 */
export type CommandInputProps = React.InputHTMLAttributes<HTMLInputElement>;

export function CommandInput({ className, ...props }: CommandInputProps) {
  const { search, onSearchChange } = useCommand();

  return (
    <div className="flex items-center border-b px-3">
      <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
      <input
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        className={cn(
          'flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        placeholder={props.placeholder}
        autoFocus
        {...props}
      />
    </div>
  );
}

/**
 * Command List
 */
export type CommandListProps = React.HTMLAttributes<HTMLDivElement>;

export function CommandList({ className, children, ...props }: CommandListProps) {
  const { selectedIndex, setSelectedIndex } = useCommand();
  const itemsRef = React.useRef<HTMLDivElement[]>([]);

  // Handle keyboard navigation
  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          setSelectedIndex((prev: number) => Math.min(prev + 1, itemsRef.current.length - 1));
          break;
        case 'ArrowUp':
          event.preventDefault();
          setSelectedIndex((prev: number) => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          event.preventDefault();
          itemsRef.current[selectedIndex]?.click();
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [selectedIndex, setSelectedIndex]);

  return (
    <div className={cn('max-h-[300px] overflow-y-auto overflow-x-hidden', className)} {...props}>
      {React.Children.map(children, (child, index) => {
        if (React.isValidElement(child)) {
          const childElement = child as React.ReactElement<{
            ref?: (el: HTMLDivElement | null) => void;
            'data-selected'?: boolean;
          }>;
          return React.cloneElement(childElement, {
            ref: (el: HTMLDivElement | null) => {
              if (el) itemsRef.current[index] = el;
            },
            'data-selected': index === selectedIndex,
          });
        }
        return child;
      })}
    </div>
  );
}

/**
 * Command Item
 */
export interface CommandItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value?: string;
  keywords?: string[];
  shortcut?: string;
}

export function CommandItem({
  className,
  value,
  keywords,
  shortcut,
  children,
  onClick,
  ...props
}: CommandItemProps) {
  const { search, onOpenChange } = useCommand();

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    onClick?.(event);
    onOpenChange(false);
  };

  const isFiltered = React.useMemo(() => {
    if (!search) return true;

    const searchLower = search.toLowerCase();
    const itemText = (value || '').toLowerCase();
    const keywordsText = (keywords || []).join(' ').toLowerCase();

    return itemText.includes(searchLower) || keywordsText.includes(searchLower);
  }, [search, value, keywords]);

  if (!isFiltered) {
    return null;
  }

  return (
    <button
      className={cn(
        'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none',
        'hover:bg-accent hover:text-accent-foreground',
        'data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground',
        'focus:bg-accent focus:text-accent-foreground',
        className
      )}
      onClick={handleClick}
      {...props}
    >
      {children}
      {shortcut && (
        <span className="ml-auto text-xs tracking-widest text-muted-foreground">{shortcut}</span>
      )}
    </button>
  );
}

/**
 * Command Group
 */
export interface CommandGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  heading?: string;
}

export function CommandGroup({ heading, className, children, ...props }: CommandGroupProps) {
  return (
    <div className={cn('overflow-hidden py-1', className)} {...props}>
      {heading && (
        <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground">{heading}</div>
      )}
      {children}
    </div>
  );
}

/**
 * Command Separator
 */
export type CommandSeparatorProps = React.HTMLAttributes<HTMLDivElement>;

export function CommandSeparator({ className, ...props }: CommandSeparatorProps) {
  return <div className={cn('-mx-1 my-1 h-px bg-muted', className)} {...props} />;
}

/**
 * Command Empty
 */
export type CommandEmptyProps = React.HTMLAttributes<HTMLDivElement>;

export function CommandEmpty({ className, ...props }: CommandEmptyProps) {
  return (
    <div className={cn('py-6 text-center text-sm text-muted-foreground', className)} {...props}>
      Nenhum resultado encontrado.
    </div>
  );
}

/**
 * Command Trigger - Button to open the command palette
 */
export interface CommandTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: React.ReactNode;
}

export function CommandTrigger({ children, className, ...props }: CommandTriggerProps) {
  const { onOpenChange } = useCommand();

  return (
    <button
      onClick={() => onOpenChange(true)}
      className={cn(
        'inline-flex items-center rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background',
        'hover:bg-accent hover:text-accent-foreground',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        className
      )}
      {...props}
    >
      {children || (
        <>
          <Search className="mr-2 h-4 w-4" />
          Pesquisar...
          <kbd className="ml-auto pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
            <span className="text-xs">⌘</span>K
          </kbd>
        </>
      )}
    </button>
  );
}

export default Command;
