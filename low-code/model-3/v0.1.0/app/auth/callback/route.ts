import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  
  // If we have a code, we can exchange it for a session
  if (code) {
    const supabase = createClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      // On success, redirect the user to the home page
      return NextResponse.redirect(origin)
    }
  }

  // On failure, or if no code is present, redirect to the login page with an error
  console.error("Authentication callback error or no code provided.");
  return NextResponse.redirect(`${origin}/login?message=Could not authenticate user. Please try again.`)
}
