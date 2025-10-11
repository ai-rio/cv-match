'use client';

import { CreditBalance } from '@/components';

/**
 * Example usage of the CreditBalance component
 *
 * This example shows how to integrate the CreditBalance component
 * into a dashboard page. The component automatically handles:
 * - Authentication state
 * - Loading states
 * - Error handling
 * - API integration with /api/users/credits
 * - Portuguese localization
 * - Responsive design
 */

export default function CreditBalanceExample() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Gerencie seus créditos e otimizações de currículo</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Credit Balance Card */}
        <div className="md:col-span-1">
          <CreditBalance />
        </div>

        {/* Other dashboard content can go here */}
        <div className="md:col-span-2 space-y-6">
          {/* Example additional cards */}
          <div className="bg-white p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-2">Recent Activity</h3>
            <p className="text-gray-600">Your recent resume optimizations will appear here.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
