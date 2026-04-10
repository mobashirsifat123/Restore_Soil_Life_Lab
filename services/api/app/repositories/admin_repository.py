from __future__ import annotations

from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


class AdminRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_users(self, organization_id: UUID) -> list[dict]:
        statement = text(
            """
            select
              u.id,
              u.organization_id,
              u.email,
              u.full_name,
              coalesce(m.role, 'org_member') as role,
              u.is_active,
              u.created_at,
              u.last_login_at
            from users u
            left join organization_memberships m
              on m.user_id = u.id
             and m.organization_id = u.organization_id
             and m.is_active = true
            where u.organization_id = :organization_id
              and u.deleted_at is null
            order by u.created_at desc, u.email asc
            """
        )
        return [dict(row) for row in self.session.execute(statement, {"organization_id": organization_id}).mappings()]

    def create_activity_log(
        self,
        *,
        organization_id: UUID | None,
        activity_type: str,
        activity_label: str,
        user_id: UUID | None = None,
        user_email: str | None = None,
        details: str | None = None,
    ) -> None:
        statement = text(
            """
            insert into user_activity_logs (
              organization_id,
              user_id,
              user_email,
              activity_type,
              activity_label,
              details,
              metadata_json
            )
            values (
              :organization_id,
              :user_id,
              :user_email,
              :activity_type,
              :activity_label,
              :details,
              '{}'::jsonb
            )
            """
        )
        self.session.execute(
            statement,
            {
                "organization_id": organization_id,
                "user_id": user_id,
                "user_email": user_email,
                "activity_type": activity_type,
                "activity_label": activity_label,
                "details": details,
            },
        )
        self.session.commit()

    def list_user_activity(self, organization_id: UUID, limit: int = 200) -> list[dict]:
        statement = text(
            """
            with activity as (
              select
                u.created_at as happened_at,
                'user_signup' as activity_type,
                'Signed up' as activity_label,
                u.id as user_id,
                u.email as user_email,
                coalesce(u.full_name, 'New member account') as details
              from users u
              where u.organization_id = :organization_id
                and u.deleted_at is null

              union all

              select
                u.last_login_at as happened_at,
                'user_signin' as activity_type,
                'Signed in' as activity_label,
                u.id as user_id,
                u.email as user_email,
                'Authenticated session created' as details
              from users u
              where u.organization_id = :organization_id
                and u.deleted_at is null
                and u.last_login_at is not null

              union all

              select
                s.revoked_at as happened_at,
                'user_signout' as activity_type,
                'Signed out' as activity_label,
                u.id as user_id,
                u.email as user_email,
                coalesce(s.user_agent, 'Session revoked') as details
              from auth_sessions s
              join users u on u.id = s.user_id
              where s.organization_id = :organization_id
                and s.revoked_at is not null

              union all

              select
                p.created_at as happened_at,
                'project_created' as activity_type,
                'Created project' as activity_label,
                u.id as user_id,
                u.email as user_email,
                p.name as details
              from projects p
              left join users u on u.id = p.created_by_user_id
              where p.organization_id = :organization_id
                and p.deleted_at is null

              union all

              select
                s.created_at as happened_at,
                'soil_sample_created' as activity_type,
                'Added soil sample' as activity_label,
                u.id as user_id,
                u.email as user_email,
                s.sample_code as details
              from soil_samples s
              left join users u on u.id = s.created_by_user_id
              where s.organization_id = :organization_id
                and s.deleted_at is null

              union all

              select
                sc.created_at as happened_at,
                'scenario_created' as activity_type,
                'Created scenario' as activity_label,
                u.id as user_id,
                u.email as user_email,
                sc.name as details
              from simulation_scenarios sc
              left join users u on u.id = sc.created_by_user_id
              where sc.organization_id = :organization_id
                and sc.deleted_at is null

              union all

              select
                r.created_at as happened_at,
                'run_submitted' as activity_type,
                'Submitted run' as activity_label,
                u.id as user_id,
                u.email as user_email,
                concat('Run ', r.id::text, ' (', r.status::text, ')') as details
              from simulation_runs r
              left join users u on u.id = r.created_by_user_id
              where r.organization_id = :organization_id

              union all

              select
                l.happened_at,
                l.activity_type,
                l.activity_label,
                l.user_id,
                coalesce(l.user_email, u.email) as user_email,
                l.details
              from user_activity_logs l
              left join users u on u.id = l.user_id
              where l.organization_id = :organization_id
            )
            select *
            from activity
            where happened_at is not null
            order by happened_at desc
            limit :limit
            """
        )
        return [
            dict(row)
            for row in self.session.execute(
                statement,
                {"organization_id": organization_id, "limit": limit},
            ).mappings()
        ]
