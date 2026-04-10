import { getServerSession } from "../../../lib/server-session";
import { BioSilkChatWidget } from "../../../components/chat/biosilk-chat-widget";

export default async function MemberChatPage() {
  const session = await getServerSession();

  return (
    <div className="mx-auto max-w-4xl py-10 px-6">
      <div className="mb-8">
        <h1 className="font-serif text-3xl font-semibold text-[#1e3318]">BioSilk Chat</h1>
        <p className="mt-2 text-[#4a5e40]">
          Your personalized assistant for soil health, pest diagnosis, and farming guidance.
        </p>
      </div>

      <div className="overflow-hidden rounded-[32px] shadow-sm border border-[rgba(58,92,47,0.12)]">
        <BioSilkChatWidget initialSession={session} mode="embedded" forceOpen={true} />
      </div>
    </div>
  );
}
