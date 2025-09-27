from flask import Blueprint, render_template, redirect, url_for, request, flash
from src.database import sman_db as get_db_connection

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE role != 'admin'")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin.html', users=users)

@admin_bp.route('/admin/promote/<int:user_id>', methods=['POST'])
def promote_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = 'admin' WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('User promoted to admin successfully.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/demote/<int:user_id>', methods=['POST'])
def demote_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = 'user' WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('User demoted to regular user successfully.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.admin_dashboard'))