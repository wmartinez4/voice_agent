"""
Update all customer phone numbers to a single test number.
"""
from database import get_supabase_client

def update_all_phones(new_phone: str):
    supabase = get_supabase_client()
    
    # Get all customers first
    result = supabase.table('customers').select('*').execute()
    
    print(f'🔄 Updating all customer phone numbers to {new_phone}')
    print('=' * 60)
    print()
    
    for customer in result.data:
        # Update phone number
        update_result = supabase.table('customers').update({
            'phone': new_phone
        }).eq('id', customer['id']).execute()
        
        print(f'✅ Updated: {customer["name"]}')
        print(f'   Old phone: {customer["phone"]}')
        print(f'   New phone: {new_phone}')
        print()
    
    print('=' * 60)
    print('✅ All customers updated successfully!')
    print()
    print('📋 Final customer list:')
    final = supabase.table('customers').select('*').execute()
    for c in final.data:
        print(f'  • {c["name"]} - {c["phone"]} - ${c["debt_amount"]} ({c["status"]})')

if __name__ == "__main__":
    update_all_phones("+573124199685")

