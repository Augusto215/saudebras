#!/usr/bin/env python
"""
Script para limpar assinaturas inválidas do Stripe
Execute com: python manage.py shell < cleanup_subscriptions.py
"""

import os
import sys
import django

# Configurar o Django
sys.path.append('/home/alvaro019/trabalho-qualitech/site-saudebras')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saudebras.settings')
django.setup()

from usuarios.models import Subscription
import stripe

def cleanup_invalid_subscriptions():
    """
    Limpa todas as assinaturas que não existem mais no Stripe
    """
    print("🔍 Iniciando verificação de assinaturas...")
    
    active_subscriptions = Subscription.objects.filter(active=True)
    total_count = active_subscriptions.count()
    invalid_count = 0
    
    print(f"📊 Total de assinaturas ativas: {total_count}")
    
    for subscription in active_subscriptions:
        try:
            # Tentar recuperar a assinatura do Stripe
            stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            print(f"✅ Assinatura válida: {subscription.stripe_subscription_id}")
            
        except stripe.error.InvalidRequestError as e:
            # Assinatura não existe mais no Stripe
            print(f"❌ Assinatura inválida encontrada: {subscription.stripe_subscription_id}")
            print(f"   Erro: {e}")
            
            # Marcar como inativa
            subscription.active = False
            subscription.save()
            invalid_count += 1
            
            # Informar qual usuário foi afetado
            if subscription.profissional:
                print(f"   📧 Profissional afetado: {subscription.profissional.email}")
            elif subscription.clinica:
                print(f"   🏥 Clínica afetada: {subscription.clinica.email}")
                
        except Exception as e:
            print(f"⚠️  Erro inesperado ao verificar {subscription.stripe_subscription_id}: {e}")
    
    print(f"\n🎯 Resultado:")
    print(f"   Total verificadas: {total_count}")
    print(f"   Inválidas encontradas: {invalid_count}")
    print(f"   Válidas: {total_count - invalid_count}")
    
    if invalid_count > 0:
        print(f"\n✨ {invalid_count} assinaturas inválidas foram marcadas como inativas.")
    else:
        print(f"\n🎉 Todas as assinaturas estão válidas!")
    
    return invalid_count

if __name__ == "__main__":
    cleanup_invalid_subscriptions()
