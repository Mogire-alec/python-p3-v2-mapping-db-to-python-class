from __init__ import CURSOR, CONN


class Department:
    
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Department instances """
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Department instances """
        sql = """
            DROP TABLE IF EXISTS departments;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the name and location values of the current Department instance.
        Update object id attribute using the primary key value of new row.
        """
        sql = """
            INSERT INTO departments (name, location)
            VALUES (?, ?)
        """

        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()

        self.id = CURSOR.lastrowid
        Department.all[self.id] = self  # Add to cache

    @classmethod
    def create(cls, name, location):
        """ Initialize a new Department instance and save the object to the database """
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Update the table row corresponding to the current Department instance."""
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Department instance"""
        sql = """
            DELETE FROM departments
            WHERE id = ?
        """

        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        
        if self.id in Department.all:
            del Department.all[self.id]
        
        # Reset id (optional but good practice)
        self.id = None
        
    @classmethod
    def instance_from_db(cls, row):
         """Convert a database row into a Department object"""
           # Check if object already exists in cache
         department = cls.all.get(row[0])  # row[0] is the id
    
         if department:
         # Update attributes in case they changed
          department.name = row[1]
          department.location = row[2]
         else:
         # Create new object and add to cache
          department = cls(row[1], row[2])  # name, location
          department.id = row[0]  # id
          cls.all[department.id] = department
    
         return department
     
    @classmethod
    def get_all(cls):
        """Return all departments as objects"""
        sql = "SELECT * FROM departments"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows] 
    
    @classmethod
    def find_by_id(cls, id):
         """Find a department by ID"""
         sql = """
            SELECT * FROM departments 
            WHERE id = ?
         """
         row = CURSOR.execute(sql, (id,)).fetchone()
         return cls.instance_from_db(row) if row else None
     
    @classmethod
    def find_by_name(cls, name):
         """Find first department with matching name"""
         sql = """
             SELECT * FROM departments 
             WHERE name = ?
         """
         row = CURSOR.execute(sql, (name,)).fetchone()
         return cls.instance_from_db(row) if row else None 
     
    def delete(self):
        """Delete from DB and remove from cache"""
        sql = "DELETE FROM departments WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
    
    # Remove from cache and reset id
        del type(self).all[self.id]
        self.id = None 