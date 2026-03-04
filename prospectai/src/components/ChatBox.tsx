import { Paperclip, Mic, Send, Link as LinkIcon, Loader2 } from 'lucide-react';
import { useMessages } from '../api/queries';

export function ChatBox() {
  const { data: messages = [], isLoading, isError } = useMessages();

  if (isLoading) {
      return (
        <div className="w-full h-[60vh] md:h-full bg-surface border border-border rounded-3xl p-2 flex flex-col items-center justify-center mx-auto shadow-soft transition-colors duration-300">
           <Loader2 className="w-8 h-8 animate-spin text-primary mb-4" />
           <p className="text-text-secondary text-sm">Synchronisation des messages...</p>
        </div>
      );
  }

  if (isError) {
      return (
        <div className="w-full h-full bg-surface border border-border rounded-3xl p-2 flex flex-col items-center justify-center mx-auto shadow-soft transition-colors duration-300">
           <div className="rounded-full bg-danger/10 p-4 mb-4">
             <span className="text-danger font-bold text-xl">!</span>
           </div>
           <p className="text-text-primary font-medium">Connexion interrompue</p>
           <p className="text-text-secondary text-sm max-w-xs text-center mt-2">Impossible de charger l'historique des messages. Vérifiez le backend.</p>
        </div>
      );
  }

  return (
    <div className="w-full h-full bg-border rounded-3xl p-2 flex flex-col mx-auto font-sans shadow-soft transition-colors duration-300">
      {/* Messages Area */}
      <div className="w-full flex-1 bg-surface rounded-2xl p-6 md:p-8 flex flex-col gap-6 overflow-y-auto transition-colors duration-300">
        
        {messages.map((msg) => (
            <div key={msg.id} className={`flex flex-col gap-2 max-w-[85%] md:max-w-[70%] ${msg.message_type === 'outbound' ? 'self-end items-end' : 'self-start'}`}>
                <div className={`flex items-center gap-2 ${msg.message_type === 'outbound' ? 'flex-row-reverse' : ''}`}>
                    <span className="text-sm font-semibold text-text-primary">
                        {msg.message_type === 'outbound' ? 'Vous' : msg.lead_contact_name}
                    </span>
                    <span className="text-xs text-text-secondary">
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                </div>
                <div className={`${msg.message_type === 'outbound' ? 'bg-primary text-white rounded-[16px_16px_2px_16px] shadow-sm' : 'bg-background text-text-primary rounded-[16px_16px_16px_2px] border border-border'} p-4 text-sm leading-relaxed transition-colors duration-300 whitespace-pre-wrap`}>
                    {msg.body}
                </div>
            </div>
        ))}
        {messages.length === 0 && (
            <div className="text-center text-text-secondary py-10">Aucun message pour le moment</div>
        )}
      </div>

      {/* Input Area */}
      <div className="mt-auto px-4 pb-4 pt-2">
        <div className="w-full h-16 bg-surface rounded-full flex items-center px-2 shadow-sm border border-border transition-colors duration-300">
          <button title="Attach file" className="w-12 h-12 flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors rounded-full hover:bg-background">
            <Paperclip className="w-5 h-5" />
          </button>
          <input 
            type="text" 
            placeholder="Tapez votre message..." 
            className="flex-1 h-full bg-transparent outline-none px-4 text-text-primary placeholder:text-text-secondary font-sans text-sm"
          />
          <button title="Voice message" className="w-12 h-12 flex items-center justify-center text-text-secondary hover:text-text-primary transition-colors rounded-full hover:bg-background">
            <Mic className="w-5 h-5" />
          </button>
          <button title="Send message" className="w-12 h-12 bg-text-primary flex items-center justify-center text-white hover:bg-black transition-colors rounded-full ml-2 shadow-sm">
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
