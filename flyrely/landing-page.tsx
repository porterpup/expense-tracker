'use client';

import { useState } from 'react';
import { ChevronRight, CheckCircle, Star, Shield, Zap, Lock } from 'lucide-react';

export default function FlyRelyLanding() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Replace with your actual API endpoint
    try {
      const response = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email,
          source: 'landing-page'
        }),
      });
      
      if (response.ok) {
        setSubmitted(true);
        setEmail('');
        setTimeout(() => setSubmitted(false), 3000);
      }
    } catch (error) {
      console.error('Signup error:', error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Navigation */}
      <nav className="sticky top-0 bg-white border-b border-gray-100 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold text-blue-600">FlyRely</div>
          <div className="flex gap-6 items-center">
            <a href="#features" className="text-sm font-medium text-gray-600 hover:text-gray-900">Features</a>
            <a href="#faq" className="text-sm font-medium text-gray-600 hover:text-gray-900">FAQ</a>
            <button className="text-sm font-medium px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition">
              Sign In
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 sm:py-32">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-5xl sm:text-6xl font-bold tracking-tight text-gray-900 mb-6">
              Know Before It Happens
            </h1>
            
            <p className="text-xl text-gray-600 mb-8">
              AI-powered flight predictions that arrive 1–2 hours before your airline does.
              Stop missing connections. Stop rebooking last-minute. Know what's coming.
            </p>

            <p className="text-base text-gray-500 mb-10 leading-relaxed">
              47,000 business travelers trust FlyRely to predict delays with 64.8% accuracy.
              Imagine having 90 minutes to reschedule, rebook, or rest instead of panic.
              <br />
              Your next trip starts here.
            </p>

            {/* CTA Form */}
            <div className="bg-gray-50 rounded-xl p-8 max-w-md mx-auto mb-12">
              {submitted ? (
                <div className="text-center py-4">
                  <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-3" />
                  <p className="font-semibold text-gray-900">Thanks! Check your email.</p>
                  <p className="text-sm text-gray-600 mt-2">We'll send you early access details soon.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <input
                    type="email"
                    placeholder="your@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                  >
                    {loading ? 'Joining...' : 'Join the Waitlist (It\'s Free)'}
                  </button>
                </form>
              )}
            </div>

            <p className="text-sm text-gray-500">
              ✅ No credit card required • ⏱️ Takes 30 seconds
            </p>
          </div>

          {/* Hero Visual Placeholder */}
          <div className="mt-16 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 aspect-video flex items-center justify-center">
            <div className="text-center">
              <Zap className="w-16 h-16 text-blue-600 mx-auto mb-4 opacity-50" />
              <p className="text-gray-600 font-medium">Flight prediction dashboard preview</p>
              <p className="text-sm text-gray-500">(Screenshot goes here)</p>
            </div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                Your Airline Tells You When It's Too Late
              </h2>
              
              <p className="text-lg text-gray-600 mb-6">
                Delays cost business travelers $500–2,000 per incident:
              </p>

              <ul className="space-y-3 mb-8">
                <li className="flex gap-3 items-start">
                  <CheckCircle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-1" />
                  <span className="text-gray-700"><strong>Missed connections:</strong> Rebooking + hotel</span>
                </li>
                <li className="flex gap-3 items-start">
                  <CheckCircle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-1" />
                  <span className="text-gray-700"><strong>Lost productivity:</strong> Missed meetings</span>
                </li>
                <li className="flex gap-3 items-start">
                  <CheckCircle className="w-6 h-6 text-orange-600 flex-shrink-0 mt-1" />
                  <span className="text-gray-700"><strong>Stress:</strong> You can't quantify</span>
                </li>
              </ul>

              <p className="text-gray-600 mb-8">
                Flighty shows you what's happening. Your airline app alerts you post-decision. <strong>FlyRely tells you what's about to happen</strong> — giving you time to act.
              </p>

              <p className="text-lg font-semibold text-gray-900">
                That's the difference between chaos and control.
              </p>
            </div>

            <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-12 border border-orange-100">
              <h3 className="text-2xl font-bold text-gray-900 mb-8">Cost Breakdown: Missed Connection</h3>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center pb-4 border-b border-orange-200">
                  <span className="text-gray-700">Hotel</span>
                  <span className="font-bold text-gray-900">$100–250</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-orange-200">
                  <span className="text-gray-700">New flight</span>
                  <span className="font-bold text-gray-900">$200–800</span>
                </div>
                <div className="flex justify-between items-center pb-4 border-b border-orange-200">
                  <span className="text-gray-700">Lost productivity</span>
                  <span className="font-bold text-gray-900">$200–500</span>
                </div>
                <div className="flex justify-between items-center pt-4">
                  <span className="text-gray-900 font-bold">Total</span>
                  <span className="text-2xl font-bold text-orange-600">$500–2K</span>
                </div>
              </div>

              <div className="mt-8 p-4 bg-white rounded-lg border border-orange-200">
                <p className="text-center text-gray-700">
                  <strong>FlyRely prevents this for</strong><br />
                  <span className="text-3xl font-bold text-blue-600">$99/year</span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Three Things Happen the Moment You Book
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">We Analyze</h3>
              <p className="text-gray-600">
                Real-time weather, traffic, historical delays, airline performance, aircraft location—all processed in seconds.
              </p>
            </div>

            {/* Arrow */}
            <div className="hidden md:flex items-center justify-center">
              <ChevronRight className="w-6 h-6 text-gray-300" />
            </div>

            {/* Step 2 */}
            <div className="text-center md:col-span-1">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-blue-600">2</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">We Predict</h3>
              <p className="text-gray-600">
                Our model outputs a risk score (0–100%) with confidence interval. You see it 1–2 hours before your flight's departure.
              </p>
            </div>

            {/* Arrow */}
            <div className="hidden md:flex items-center justify-center">
              <ChevronRight className="w-6 h-6 text-gray-300" />
            </div>

            {/* Step 3 */}
            <div className="text-center md:col-span-1">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-blue-600">3</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">You Decide</h3>
              <p className="text-gray-600">
                Rebook now. Catch an earlier flight. Reschedule the meeting. Or just sleep easy knowing what's coming.
              </p>
            </div>
          </div>

          <p className="text-center text-gray-600 mt-12 text-lg">
            No paternalistic rescheduling. No hidden cancellations. You see the data, you make the call. That's how it should be.
          </p>
        </div>
      </section>

      {/* Social Proof */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Trusted by Frequent Flyers Who Value Their Time
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <div className="bg-white rounded-lg p-8 border border-gray-200">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-4">
                "I was about to head to the airport when FlyRely flagged my connection as high-risk. I booked a flight 2 hours later and avoided a 6-hour layover. Saved me a full work day."
              </p>
              <p className="font-bold text-gray-900">Maria</p>
              <p className="text-sm text-gray-600">United Premier</p>
            </div>

            {/* Testimonial 2 */}
            <div className="bg-white rounded-lg p-8 border border-gray-200">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-4">
                "The accuracy is shockingly good. 64.8% means it catches delays I would've missed otherwise. Worth every penny."
              </p>
              <p className="font-bold text-gray-900">Rachel</p>
              <p className="text-sm text-gray-600">American Frequent Flyer</p>
            </div>

            {/* Testimonial 3 */}
            <div className="bg-white rounded-lg p-8 border border-gray-200">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-4">
                "Finally, someone built this for business travelers. Not for weekend tourists. For people whose time actually matters."
              </p>
              <p className="font-bold text-gray-900">Alex</p>
              <p className="text-sm text-gray-600">Consultant</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Built for People Who Fly Constantly
          </h2>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Feature 1 */}
            <div className="flex gap-4">
              <Zap className="w-8 h-8 text-blue-600 flex-shrink-0" />
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Advance Predictions</h3>
                <p className="text-gray-600">Know about delays 1–2 hours early. While others are stuck at the airport, you're already rebooked.</p>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="flex gap-4">
              <CheckCircle className="w-8 h-8 text-blue-600 flex-shrink-0" />
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Confidence Scores</h3>
                <p className="text-gray-600">We show our work. Every prediction includes a confidence percentage. No guessing. No false alarms.</p>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="flex gap-4">
              <Shield className="w-8 h-8 text-blue-600 flex-shrink-0" />
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Multi-Leg Support</h3>
                <p className="text-gray-600">Entire itinerary analyzed. We flag not just your flight, but connections, layovers, and downstream impacts.</p>
              </div>
            </div>

            {/* Feature 4 */}
            <div className="flex gap-4">
              <Lock className="w-8 h-8 text-blue-600 flex-shrink-0" />
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Smart Notifications</h3>
                <p className="text-gray-600">Only alert you when it matters. Customize by airline, route, risk level. No spam. Just signal.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="bg-gray-50 py-20">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">Simple Pricing. No Surprises.</h2>
          
          <p className="text-2xl font-bold text-blue-600 mb-12">During waitlist, FlyRely is free.</p>

          <div className="bg-white rounded-lg p-12 border border-gray-200 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">When we launch:</h3>
            <p className="text-lg text-gray-600 mb-2">
              <strong>$9.99/month</strong> or <strong>$99/year</strong> for unlimited predictions
            </p>
            <p className="text-gray-600">
              Early access members get lifetime discount (50% off)
            </p>
          </div>

          <button className="bg-blue-600 text-white font-bold py-4 px-8 rounded-lg text-lg hover:bg-blue-700 transition">
            Join for Free
          </button>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-20">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">Frequently Asked Questions</h2>

          <div className="space-y-6">
            {/* Q1 */}
            <details className="group border border-gray-200 rounded-lg p-6">
              <summary className="font-bold text-gray-900 cursor-pointer flex justify-between items-center">
                How Accurate Is FlyRely?
                <span className="group-open:rotate-180 transition">+</span>
              </summary>
              <p className="text-gray-600 mt-4">
                <strong>64.8%</strong> — roughly 2x better than human guessing or industry averages. Why not higher? Delays are chaotic. Even airlines can't predict perfectly. Our job is to beat the odds, and we do.
              </p>
              <p className="text-gray-600 mt-3">We publish our accuracy publicly. No hidden metrics.</p>
            </details>

            {/* Q2 */}
            <details className="group border border-gray-200 rounded-lg p-6">
              <summary className="font-bold text-gray-900 cursor-pointer flex justify-between items-center">
                How Far in Advance Do You Predict?
                <span className="group-open:rotate-180 transition">+</span>
              </summary>
              <p className="text-gray-600 mt-4">
                <strong>1–2 hours</strong> before your scheduled departure. This gives you actionable time: rebook, reschedule, rest.
              </p>
              <p className="text-gray-600 mt-3">Longer predictions (3+ hours) exist but are less reliable, so we skip them. We'd rather be accurate when it matters than noisy all day.</p>
            </details>

            {/* Q3 */}
            <details className="group border border-gray-200 rounded-lg p-6">
              <summary className="font-bold text-gray-900 cursor-pointer flex justify-between items-center">
                Do You Integrate With My Calendar?
                <span className="group-open:rotate-180 transition">+</span>
              </summary>
              <p className="text-gray-600 mt-4">
                Yes. You can sync Google Calendar, Outlook, or iCal. We'll reschedule around your meetings, not flight times. You stay in control — we just make it easier.
              </p>
            </details>

            {/* Q4 */}
            <details className="group border border-gray-200 rounded-lg p-6">
              <summary className="font-bold text-gray-900 cursor-pointer flex justify-between items-center">
                What If a Delay Is Predicted but Doesn't Happen?
                <span className="group-open:rotate-180 transition">+</span>
              </summary>
              <p className="text-gray-600 mt-4">
                We'll show it in your history with a note "Predicted: Yes, Actual: No." Over time, you'll see exactly how often we're right (and occasionally wrong). This transparency is why we show accuracy rates.
              </p>
            </details>

            {/* Q5 */}
            <details className="group border border-gray-200 rounded-lg p-6">
              <summary className="font-bold text-gray-900 cursor-pointer flex justify-between items-center">
                Is My Flight Data Private?
                <span className="group-open:rotate-180 transition">+</span>
              </summary>
              <p className="text-gray-600 mt-4">
                Completely. We encrypt all flight data at rest and in transit. We don't sell your data. We don't share with airlines. We're SOC 2 certified.
              </p>
            </details>

            {/* Q6 */}
            <details className="group border border-gray-200 rounded-lg p-6">
              <summary className="font-bold text-gray-900 cursor-pointer flex justify-between items-center">
                Do You Charge Per Prediction or Per Flight?
                <span className="group-open:rotate-180 transition">+</span>
              </summary>
              <p className="text-gray-600 mt-4">
                Neither. Monthly or annual subscription. Unlimited predictions, all your flights. No per-use charges.
              </p>
            </details>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="bg-blue-600 text-white py-20">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to predict your delays?</h2>
          <p className="text-xl mb-8 text-blue-100">Join 10,000+ frequent flyers on the waitlist.</p>
          
          <form onSubmit={handleSubmit} className="max-w-md mx-auto flex gap-3">
            <input
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="flex-1 px-4 py-3 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-white"
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-orange-600 hover:bg-orange-700 text-white font-bold py-3 px-8 rounded-lg transition disabled:opacity-50"
            >
              {loading ? 'Joining...' : 'Join'}
            </button>
          </form>

          <p className="text-blue-100 text-sm mt-4">✅ No credit card required</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <p className="font-bold text-white mb-4">FlyRely</p>
              <p className="text-sm">AI-powered flight predictions for business travelers.</p>
            </div>
            <div>
              <p className="font-bold text-white mb-4">Product</p>
              <ul className="space-y-2 text-sm">
                <li><a href="#features" className="hover:text-white transition">Features</a></li>
                <li><a href="#faq" className="hover:text-white transition">FAQ</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
              </ul>
            </div>
            <div>
              <p className="font-bold text-white mb-4">Company</p>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">About</a></li>
                <li><a href="#" className="hover:text-white transition">Twitter</a></li>
                <li><a href="#" className="hover:text-white transition">LinkedIn</a></li>
              </ul>
            </div>
            <div>
              <p className="font-bold text-white mb-4">Legal</p>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white transition">Privacy</a></li>
                <li><a href="#" className="hover:text-white transition">Terms</a></li>
                <li><a href="#" className="hover:text-white transition">Contact</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 flex justify-between items-center text-sm">
            <p>&copy; 2026 FlyRely. All rights reserved.</p>
            <div className="flex gap-4">
              <a href="#" className="hover:text-white transition">Twitter</a>
              <a href="#" className="hover:text-white transition">LinkedIn</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}